#coding: utf-8
from __future__ import unicode_literals
import jinja2
import os
import subprocess


ATOM_TEMPLATE = '''<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>{{ title|e }}</title>
  <link href="{{ link|e }}" />
  <updated>{{ updated|e }}</updated>
  <id>{{ id|e }}</id>

  {% for entry in entries %}
    <entry>
      <title>{{ entry.title|e }}</title>
      <link href="{{ entry.link }}"/>
      <id>{{ id|e }}</id>
      <updated>{{ entry.updated|e }}</updated>
      <summary>{{ entry.summary|e }}</summary>
      <author>
        <name>{{ entry.author.name|e }}</name>
        <email>{{ entry.author.email|e }}</email>
      </author>
    </entry>
  {% endfor %}
</feed>
'''


def make_atom(**kwargs):
    template = jinja2.Template(ATOM_TEMPLATE)
    return template.render(**kwargs)


# 便利関数
class CDContext(object):

    def __init__(self, cwd):
        self._cwd = cwd

    def __enter__(self):
        self._old_cwd = os.getcwd()
        os.chdir(self._cwd)

    def __exit__(self, exception, value, traceback):
        os.chdir(self._old_cwd)
        return False


def cd(cwd):
    return CDContext(cwd)


def run(command, shell=True, check=True):
    call = subprocess.check_call if check else subprocess.call
    return call(command, shell=shell)


def run_with_output(command, shell=True, check=True):
    p = subprocess.Popen(command, shell=shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    if check:
        if p.returncode != 0:
            raise Exception('return code is non-zero: {}'.format(p.returncode))
    return p.returncode, unicode(stdout, encoding='utf-8', errors='ignore'), unicode(stderr, encoding='utf-8', errors='ignore')


class GitAtom(object):

    def __init__(self, is_target, get_title, get_link):
        self._is_target = is_target
        self._get_title = get_title
        self._get_link = get_link

    def _get_content(self, commit, file):
        exitcode, output, _ = run_with_output('git show {commit}:{file}'.format(**locals()), check=False)
        return output if exitcode == 0 else ''

    def _file_to_entry(self, commit, file, author_name, author_email, updated):
        content = self._get_content(commit, file)
        if not self._is_target(commit, file, content):
            return None

        title = self._get_title(commit, file, content)
        link = self._get_link(commit, file, content)
        id = commit + ':' + file

        _, summary, _ = run_with_output('git diff {commit}^ {commit} -- {file}'.format(**locals()))

        return {
            'title': title,
            'link': link,
            'id': id,
            'updated': updated,
            'summary': summary,
            'author': {
                'name': author_name,
                'email': author_email,
            }
        }

    def _hash_to_entries(self, commit):
        _, author_name, _ = run_with_output('git show {commit} -s --format=%aN'.format(**locals()))
        _, author_email, _ = run_with_output('git show {commit} -s --format=%aE'.format(**locals()))
        _, updated, _ = run_with_output('git show {commit} -s --format=%ai'.format(**locals()))
        _, files_str, _ = run_with_output('git diff {commit}^ {commit} --name-only'.format(**locals()))
        files = files_str[:-1].split('\n')
        entries = filter(None, [self._file_to_entry(commit, file, author_name[:-1], author_email[:-1], updated[:-1]) for file in files])
        return entries

    def git_to_atom(self, cwd, title, link):
        with cd(cwd):
            _, commits_str, _ = run_with_output('git log -5 --format=%H')
            commits = commits_str[:-1].split('\n')
            entries = []
            for commit in commits:
                entries += self._hash_to_entries(commit)

            if len(entries) == 0:
                updated = '2000-01-01 00:00:00'
                id = 'no entry'
            else:
                updated = entries[0]['updated']
                id = entries[0]['id']

            dic = {
                'title': title,
                'link': link,
                'updated': updated,
                'id': id,
                'entries': entries,
            }
            return make_atom(**dic)
