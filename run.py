#!/usr/bin/env python
#coding: utf-8
from __future__ import unicode_literals
import os
import re
import markdown
import sys
import importlib
import jinja2
import atom


if len(sys.argv) != 2:
    print '{} <setting>'.format(sys.argv[0])
    sys.exit(0)

settings = importlib.import_module(sys.argv[1])


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
    md_data = unicode(open(os.path.join(settings.INPUT_DIR, path + '.md')).read(), encoding='utf-8')
    body = md_to_html(md_data, path)

    dst_dir = os.path.dirname(os.path.join(settings.OUTPUT_DIR, path))
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
    html_data = template.render(body=body, **context)
    if settings.USE_MINIFY:
        import htmlmin
        html_data = htmlmin.minify(html_data)
    open(os.path.join(settings.OUTPUT_DIR, path + '.html'), 'w').write(html_data.encode('utf-8'))


def target_paths():
    for root, dirs, files in os.walk(settings.INPUT_DIR):
        for f in files:
            if f.endswith('.md'):
                path = os.path.join(root, f)[len(settings.INPUT_DIR):].lstrip('/')
                # 更新対象でないファイルは無視する
                if re.match('^([A-Z].*)|(.*!(\.md))$', path.split('/')[-1]):
                    continue
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
    md_data = open(os.path.join(settings.INPUT_DIR, path + '.md')).read()
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

    def set_active(self, paths):
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

    def __init__(self, paths, sidebar):
        self._headers = []
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
    def is_target(commit, file, content):
        if file.endswith('.md'):
            # 更新対象でないファイルは無視する
            if re.match('^([A-Z].*)|(.*!(\.md))$', file.split('/')[-1]):
                return False
            return True

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
    return atom.GitAtom(is_target, get_title, get_link, get_html_content).git_to_atom(settings.INPUT_DIR, title, settings.BASE_URL)


def main():
    pageinfos = [make_pageinfo(path) for path in target_paths()]
    sidebar = make_sidebar(pageinfos)
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(settings.PAGE_TEMPLATE_DIR))
    template = env.get_template('content.html')
    for pageinfo in pageinfos:
        print(pageinfo['path'])
        sidebar.set_active(pageinfo['paths'])
        content_header = ContentHeader(pageinfo['paths'], sidebar)
        convert(pageinfo['path'], template, {
            'title': pageinfo['title'] + settings.TITLE_SUFFIX,
            'sidebar': sidebar,
            'content_header': content_header,
            'brand': unicode(settings.BRAND, encoding='utf-8'),
            'search': settings.GOOGLE_SITE_SEARCH,
            'analytics': settings.GOOGLE_ANALYTICS,
            'rss': settings.BASE_URL + '/' + settings.RSS_PATH,
        })
    with open(os.path.join(settings.OUTPUT_DIR, settings.RSS_PATH), 'w') as f:
        f.write(make_atom().encode('utf-8'))


if __name__ == '__main__':
    main()
