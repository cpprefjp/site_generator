#!/usr/bin/env python
#coding: utf-8
from __future__ import unicode_literals
import os
import re
import json
import sys
import importlib
import subprocess
import glob
import markdown
import jinja2
import atom


if len(sys.argv) < 2:
    print '{} <setting> [--all]'.format(sys.argv[0])
    sys.exit(0)

settings = importlib.import_module(sys.argv[1])
CONVERT_ALL = '--all' in sys.argv[2:]
CACHE_FILE = sys.argv[1] + '.cache'


def make_md_path(path):
    return os.path.join(settings.INPUT_DIR, path + '.md')


def make_html_path(path):
    return os.path.join(settings.OUTPUT_DIR, path + '.html')


def md_to_html(md_data, path):
    paths = path.split('/')

    qualified_fenced_code = 'markdown_to_html.qualified_fenced_code'
    html_attribute = 'markdown_to_html.html_attribute(base_url={base_url}, base_path={base_path}, full_path={full_path}, extension={extension})'.format(
        base_url=settings.BASE_URL,
        base_path='/'.join(paths[:-1]),
        full_path=path + '.md',
        extension='.html',
    )
    # footer = 'markdown_to_html.footer(url={url})'.format(
    #     url=settings.EDIT_URL_FORMAT.format(
    #         paths=path + '.md',
    #     )
    # )

    md = markdown.Markdown([
        'tables',
        qualified_fenced_code,
        'codehilite(noclasses=True)',
        html_attribute])
    return md.convert(md_data)


def convert(path, template, context):
    md_data = unicode(open(make_md_path(path)).read(), encoding='utf-8')
    body = md_to_html(md_data, path)

    dst_dir = os.path.dirname(os.path.join(settings.OUTPUT_DIR, path))
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
    html_data = template.render(body=body, **context)
    if settings.USE_MINIFY:
        import htmlmin
        html_data = htmlmin.minify(html_data)
    open(make_html_path(path), 'w').write(html_data.encode('utf-8'))


def is_target(path):
    # .md ファイルでなかったり、
    # 大文字のみの .md ファイルは変換しない
    if not path.endswith('.md'):
        return False
    if re.match(r'^[A-Z]+\.md$', path.split('/')[-1]):
        return False
    return True


def target_paths():
    for root, dirs, files in os.walk(settings.INPUT_DIR):
        for f in files:
            path = os.path.join(root, f)[len(settings.INPUT_DIR):].lstrip('/')
            if is_target(path):
                # .md を取り除く
                path = path[:-3]
                yield path


_HASH_HEADER_RE = re.compile(r'^( *?\n)*#(?P<header>.*?)#*(\n|$)(?P<remain>(.|\n)*)', re.MULTILINE)
_SETEXT_HEADER_RE = re.compile(r'^( *?\n)*(?P<header>.*?)\n=+[ ]*(\n|$)(?P<remain>(.|\n)*)', re.MULTILINE)


def split_title(md):
    r"""先頭の見出し部分を（あるなら）取り出す
    >>> md = '''
    ... # header
    ...
    ... contents
    ... '''
    >>> split_title(md)
    ('header', '\ncontents\n')
    >>> md = '''
    ... header
    ... ======
    ...
    ... contents
    ... '''
    >>> split_title(md)
    ('header', '\ncontents\n')
    >>> md = '''
    ... contents
    ... '''
    >>> split_title(md)
    (None, '\ncontents\n')
    """
    m = _HASH_HEADER_RE.match(md)
    if m is None:
        m = _SETEXT_HEADER_RE.match(md)
    if m is None:
        return None, md
    return m.group('header').strip(), m.group('remain')


def make_pageinfo(path):
    paths = path.split('/')
    md_data = open(make_md_path(path)).read()
    title, md = split_title(md_data)
    if title is None:
        title = paths[-1]
    title = unicode(title, encoding='utf-8')
    return {
        'path': path,
        'paths': paths,
        'href': '/' + path + '.html',
        'title': title,
    }


class Sidebar(object):

    def __init__(self):
        self._children = {}
        self.href = None
        self.title = ''
        self.name = ''
        self.active = []
        self.opened = False

    @property
    def is_node(self):
        return len(self._children) != 0

    @property
    def children(self):
        return sorted(self._children.values(), key=lambda x: (x.is_node, x.name))

    def set_pageinfo(self, paths, href, title, *args, **kwargs):
        sidebar = self
        for path in paths:
            if path not in sidebar._children:
                child = Sidebar()
                child.name = path
                child.title = path
                sidebar._children[path] = child
            sidebar = sidebar._children[path]
        sidebar.name = paths[-1]
        sidebar.href = href
        sidebar.title = title

    def contains(self, paths):
        sidebar = self
        for path in paths:
            if path not in sidebar._children:
                return False
            sidebar = sidebar._children[path]
        return True

    def set_active(self, paths):
        if not self.contains(paths):
            return

        sidebar = self
        for path in self.active:
            sidebar = sidebar._children[path]
            sidebar.opened = False

        sidebar = self
        for path in paths:
            sidebar = sidebar._children[path]
            sidebar.opened = True

        self.active = paths


def make_sidebar(pageinfos):
    sidebar = Sidebar()
    for pageinfo in pageinfos:
        sidebar.set_pageinfo(**pageinfo)
    return sidebar


class ContentHeader(object):

    def __init__(self, paths, sidebar, sidebar_index):
        self._headers = []
        if sidebar_index:
            last = len(paths) == 1 and paths[0] == 'index'
            self._headers.append({
                'name': 'index',
                'is_active': last,
                'href': sidebar_index.href,
                'title': sidebar_index.title,
            })
            if last:
                return

        for i in range(len(paths)):
            path = paths[i]
            last = i == len(paths) - 1
            child = sidebar._children[path]
            self._headers.append({
                'name': path,
                'is_active': last,
                'href': child.href,
                'title': child.title,
            })
            sidebar = child

    @property
    def headers(self):
        return self._headers


def make_atom():
    def is_target_(commit, file, content):
        return is_target(file)

    def get_title(commit, file, content):
        title, md = split_title(content)
        if title is None:
            title = file.split('/')[-1]
        return title

    def get_link(commit, file, content):
        return settings.BASE_URL + '/' + file[:-3] + '.html'

    def get_html_content(commit, file, content):
        return md_to_html(content, file[:-3]) if content else ''

    title = unicode(settings.BRAND, encoding='utf-8')
    return atom.GitAtom(is_target_, get_title, get_link, get_html_content).git_to_atom(settings.INPUT_DIR, title, settings.BASE_URL)


class Cache(object):

    def __init__(self, cache_file):
        try:
            self._cache = json.loads(open(cache_file).read())
        except:
            self._cache = {}
        self._cache_file = cache_file

    def convert_required(self, path):
        if path not in self._cache:
            return True
        cache = self._cache[path]

        if 'md_lastmodify' not in cache:
            return True
        if 'html_lastmodify' not in cache:
            return True

        md_path = make_md_path(path)
        if not os.path.exists(md_path):
            return True
        if os.path.getmtime(md_path) != cache['md_lastmodify']:
            return True

        html_path = make_html_path(path)
        if not os.path.exists(html_path):
            return True
        if os.path.getmtime(html_path) != cache['html_lastmodify']:
            return True

        return False

    def converted(self, path):
        md_path = make_md_path(path)
        html_path = make_html_path(path)
        self._cache[path] = {
            'md_lastmodify': os.path.getmtime(md_path),
            'html_lastmodify': os.path.getmtime(html_path),
        }

    def flush(self):
        with open(self._cache_file, 'w') as f:
            f.write(json.dumps(self._cache))


# 不要な html を削除する
# static ファイルや rss も消えるが、この後生成するので気にしない
def remove_not_target_paths(paths):
    html_path_set = set(map(make_html_path, paths))
    for root, dirs, files in os.walk(settings.OUTPUT_DIR):
        if '/.git' in root:
            continue

        for f in files:
            target_file_path = os.path.join(root, f)
            if target_file_path not in html_path_set:
                print('remove: ' + target_file_path)
                os.remove(target_file_path)
    # 空ディレクトリの削除
    for root, dirs, files in os.walk(settings.OUTPUT_DIR, topdown=False):
        if '/.git' in root:
            continue

        if len(files) == 0:
            try:
                os.rmdir(root)
                print('remove directory: ' + root)
            except:
                pass


def main():
    pageinfos = [make_pageinfo(path) for path in target_paths()]
    sidebar = make_sidebar(pageinfos)
    if 'index' in sidebar._children:
        sidebar_index = sidebar._children['index']
        del sidebar._children['index']
    else:
        sidebar_index = None

    cache = Cache(CACHE_FILE)
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(settings.PAGE_TEMPLATE_DIR))
    template = env.get_template('content.html')
    for pageinfo in pageinfos:
        required = cache.convert_required(pageinfo['path'])
        if not CONVERT_ALL and not required:
            # print(pageinfo['path'] + ' -- already converted')
            continue
        if CONVERT_ALL and not required:
            print(pageinfo['path'] + ' -- force converting')
        else:
            print(pageinfo['path'])
        sidebar.set_active(pageinfo['paths'])
        content_header = ContentHeader(pageinfo['paths'], sidebar, sidebar_index)
        convert(pageinfo['path'], template, {
            'title': pageinfo['title'] + settings.TITLE_SUFFIX,
            'sidebar': sidebar,
            'content_header': content_header,
            'brand': unicode(settings.BRAND, encoding='utf-8'),
            'search': settings.GOOGLE_SITE_SEARCH,
            'analytics': settings.GOOGLE_ANALYTICS,
            'rss': settings.BASE_URL + '/' + settings.RSS_PATH,
            'edit_url': settings.EDIT_URL_FORMAT.format(path=pageinfo['path'] + '.md'),
            'history_url': settings.HISTORY_URL_FORMAT.format(path=pageinfo['path'] + '.md'),
            'project_url': settings.PROJECT_URL,
            'project_name': settings.PROJECT_NAME,
        })
        cache.converted(pageinfo['path'])
    cache.flush()
    remove_not_target_paths(pageinfo['path'] for pageinfo in pageinfos)

    with open(os.path.join(settings.OUTPUT_DIR, settings.RSS_PATH), 'w') as f:
        f.write(make_atom().encode('utf-8'))

    # 静的ファイルをコピーする
    subprocess.call(['cp', '-v', '-r'] + glob.glob(os.path.join(settings.STATIC_DIR, '*')) + [settings.OUTPUT_DIR])


if __name__ == '__main__':
    main()
