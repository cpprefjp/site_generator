#coding: utf-8
from __future__ import unicode_literals
import jinja2
import os
import subprocess


SITEMAP_TEMPLATE = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  {% for entry in entries %}
    <url>
      <loc>{{ entry.loc }}</loc>
      <lastmod>{{ entry.lastmod|e }}</lastmod>
      <changefreq>daily</changefreq>
      <priority>{{ entry.priority }}</priority>
    </url>
  {% endfor %}
</urlset>
'''


def make_sitemap(**kwargs):
    template = jinja2.Template(SITEMAP_TEMPLATE)
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


class GitSitemap(object):

    def __init__(self, get_loc, get_priority, get_default_datetime):
        self._get_loc = get_loc
        self._get_priority = get_priority
        self._get_default_datetime = get_default_datetime

    def _get_last_commit_times(self):
        prefix = '---- '
        _, logs, _ = run_with_output(['git', 'log', '-m', '-r', '--name-only', '--format=' + prefix + '%ai'], shell=False)
        dic = dict()
        for line in logs.split('\n'):
            line = line.strip()
            if line.startswith(prefix):
                dt = line[len(prefix):]
                xs = dt.split(' ')
                # 2015-02-13 00:10:04 +0900
                # to
                # 2015-02-13T00:10:04+09:00
                dt = xs[0] + 'T' + xs[1] + xs[2][:3] + ':' + xs[2][3:]
            elif len(line) != 0:
                if line not in dic:
                    dic[line] = dt
        return dic

    def _pageinfo_to_entry(self, times, pageinfo):
        mdpath = pageinfo['path'] + '.md'
        if mdpath not in times:
            return None
        loc = self._get_loc(pageinfo)
        lastmod = max(times[mdpath], self._get_default_datetime(pageinfo))
        priority = self._get_priority(pageinfo)

        if priority > 1.0:
            priority = 1.0
        if priority < 0.1:
            priority = 0.1
        return {
            'loc': loc,
            'lastmod': lastmod,
            'priority': priority,
        }

    def git_to_sitemap(self, cwd, pageinfos):
        with cd(cwd):
            times = self._get_last_commit_times()
            entries = filter(None, [self._pageinfo_to_entry(times, pageinfo) for pageinfo in pageinfos])
            dic = {
                'entries': entries,
            }
            return make_sitemap(**dic)
