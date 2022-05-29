#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
import glob
import importlib
import json
import os
import posixpath
import re
import subprocess
import sys
import time

import atom

import jinja2

import markdown

import markdown_to_html.meta

import sitemap


if len(sys.argv) < 2:
    print('{} <setting> [--all] [--prefix=<target>] [--concurrency=<num>]'.format(sys.argv[0]))
    sys.exit(0)

settings = importlib.import_module(sys.argv[1])
CONVERT_ALL = '--all' in sys.argv[2:]
CACHE_FILE = sys.argv[1] + '.cache'
TARGET_PREFIX = [x[len('--prefix='):] for x in sys.argv[2:] if x.startswith('--prefix=')]
TARGET_PREFIX = TARGET_PREFIX[0] if TARGET_PREFIX else ''
CONCURRENCY = [int(x[len('--concurrency='):]) for x in sys.argv[2:] if x.startswith('--concurrency=')]
CONCURRENCY = CONCURRENCY[0] if CONCURRENCY else 2

if settings.CACHEBUST_TYPE == 'none':
    _CACHEBUST = ''
elif settings.CACHEBUST_TYPE == 'time':
    _CACHEBUST = '?cachebust=' + str(int(round(time.time() * 1000)))
elif settings.CACHEBUST_TYPE == 'git':
    stdout = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=settings.CACHEBUST_DIR, text=True, errors='ignore')
    _CACHEBUST = '?cachebust=' + stdout.strip()
else:
    raise RuntimeError('Invalid _CACHEBUST {}'.format(_CACHEBUST))


def make_md_path(path):
    return os.path.join(settings.INPUT_DIR, path + '.md')


def make_html_path(path):
    return os.path.join(settings.OUTPUT_DIR, path + '.html')


_SWAP_A_AND_CODE_RE = re.compile(r'<(a|span)\b([^>]*)><code>([^<]*)</code>(</\1>)')
_MERGE_ADJACENT_CODE_RE = re.compile(r'</code>( ?)<code>')


def md_to_html(md_data, path, hrefs=None, global_qualify_list=None):
    paths = path.split('/')

    extension_configs = {}
    extension_configs['markdown_to_html.qualified_fenced_code'] = {
        'global_qualify_list': global_qualify_list
    }
    extension_configs['markdown_to_html.html_attribute'] = {
        'base_url': settings.BASE_URL,
        'base_path': '/'.join(paths[:-1]),
        'full_path': path + '.md',
        'extension': '.html',
        'use_relative_link': settings.USE_RELATIVE_LINK,
    }
    extension_configs['codehilite'] = {
        'noclasses': False
    }
    # footer = 'markdown_to_html.footer(url={url})'.format(
    #     url=settings.EDIT_URL_FORMAT.format(
    #         paths=path + '.md',
    #     )
    # )

    md = markdown.Markdown(extensions=[
        'tables',
        'markdown_to_html.meta',
        'markdown_to_html.mathjax',
        'markdown_to_html.qualified_fenced_code',
        'codehilite',
        'markdown_to_html.html_attribute'],
        extension_configs=extension_configs)
    md._html_attribute_hrefs = hrefs

    html = md.convert(md_data)
    html = _SWAP_A_AND_CODE_RE.sub(r'<code><\1\2>\3</\1></code>', html)
    html = _MERGE_ADJACENT_CODE_RE.sub(r'\1', html)
    return html, {
        'meta_result': md._meta_result,
        'example_codes': md._example_codes,
        'mathjax_enabled': md._mathjax_enabled
    }


_TAG_RE = re.compile('<.+?>')


def remove_tags(html):
    return _TAG_RE.sub('', html)


def convert(path, template, context, hrefs, global_qualify_list):
    with open(make_md_path(path), encoding='utf-8') as f:
        md_data = f.read()
    body, info = md_to_html(md_data, path, hrefs, global_qualify_list)
    meta = info['meta_result']
    codes = info['example_codes']
    mdinfo = {
        'meta': meta,
        'sources': [{'id': code['id'], 'source': code['code']} for code in codes],
        'page_id': path.split('/'),
    }

    if 'class' in meta:
        context['title'] = meta['class'][0] + '::' + context['title']
    context['keywords'] += ',' + ','.join(value[0] for value in meta.values())
    context['mdinfo'] = json.dumps(mdinfo)

    if context['description'] is None:
        context['description'] = remove_tags(body)
    context['description'] = context['description'].replace('\n', ' ')[:200]

    context['mathjax'] = info['mathjax_enabled']
    dst_dir = os.path.dirname(os.path.join(settings.OUTPUT_DIR, path))
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
    html_data = template.render(body=body, **context)
    if settings.USE_MINIFY:
        import htmlmin
        html_data = htmlmin.minify(html_data)
    with open(make_html_path(path), 'w', encoding='utf-8') as f:
        f.write(html_data)


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
_REMOVE_ESCAPE_RE = re.compile(r'\\(.)')


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
    return _REMOVE_ESCAPE_RE.sub(r'\1', m.group('header').strip()), m.group('remain')


def get_meta(md):
    """メタ情報を取り出す"""
    result = {}
    lines = md.split('\n')
    for line in lines:
        m = markdown_to_html.meta.META_RE.match(line)
        if m is not None:
            target = m.group('target')
            name = m.group('name')
            if name not in result:
                result[name] = []
            result[name].append(target)
    return result


_DESCRIPTION_RE = re.compile(r'#.*?概要.*?\n(?P<description>.*?)(\n#|$)', re.MULTILINE)


def get_description(md):
    m = _DESCRIPTION_RE.search(md)
    if m is not None:
        return m.group('description')


def make_pageinfo(path):
    paths = path.split('/')
    md_data = None
    try:
        with open(make_md_path(path), encoding='utf-8') as f:
            md_data = f.read()
    except Exception:
        print('open file error : {}'.format(path))
        raise

    title, md = split_title(md_data)
    if title is None:
        title = paths[-1]
    title = title
    meta = get_meta(md_data)
    description = get_description(md)
    return {
        'path': path,
        'paths': paths,
        'href': '/' + path + '.html',
        'title': title,
        'meta': meta,
        'is_index': len(paths) == 1 and paths[0] == 'index',
        'description': description,
    }


class Sidebar(object):

    def __init__(self):
        self._children = {}
        self.href = None
        self.title = ''
        self.name = ''
        self.meta = {}
        self.active = []
        self.opened = False

    @property
    def is_node(self):
        return len(self._children) != 0

    @property
    def children(self):
        return sorted(self._children.values(), key=lambda x: (x.is_node, settings.get_order_priority(x.name), x.name))

    CPP_DIC = markdown_to_html.meta.MetaPostprocessor.CPP_DIC

    @property
    def encoded_cpp_meta(self):
        html = ''
        if 'cpp' in self.meta:
            for name in self.meta['cpp']:
                html = '<span class="cpp-sidebar {class_name}" title="{title}">{text}</span>'.format(**self.CPP_DIC[name]) + html
        if len(html) == 0:
            return ''
        else:
            return ' ' + html

    def set_pageinfo(self, paths, href, title, meta, *args, **kwargs):
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
        sidebar.meta = meta

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
        return md_to_html(content, file[:-3])[0] if content else ''

    title = settings.BRAND
    return atom.GitAtom(is_target_, get_title, get_link, get_html_content).git_to_atom(settings.INPUT_DIR, title, settings.BASE_URL)


def make_sitemap(pageinfos):
    def get_loc(pageinfo):
        return settings.BASE_URL + pageinfo['href']

    def get_priority(pageinfo):
        if pageinfo['path'] == 'index':
            return 1.0
        depth = len(pageinfo['paths'])
        return (10 - depth) / 10

    info = get_self_latest_commit_info()

    def get_default_datetime(pageinfo):
        xs = info['last_updated'].split(' ')
        # 2015-02-13 00:10:04 +0900
        # to
        # 2015-02-13T00:10:04+09:00
        return xs[0] + 'T' + xs[1] + xs[2][:3] + ':' + xs[2][3:]

    return sitemap.GitSitemap(get_loc, get_priority, get_default_datetime).git_to_sitemap(settings.INPUT_DIR, pageinfos)


class Cache(object):

    def __init__(self, cache_file):
        try:
            with open(cache_file, encoding='utf-8') as f:
                self._cache = json.loads(f.read())
        except Exception:
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
        with open(self._cache_file, 'w', encoding='utf-8') as f:
            f.write(json.dumps(self._cache))


def get_latest_commit_info(path):
    commit_log = subprocess.check_output(['git', 'log', '-1', '--date=iso', '--pretty=format:%at %an', path + '.md'], cwd=settings.INPUT_DIR, text=True, errors='ignore')
    if not commit_log:
        return None
    timestamp, author = commit_log.split(' ', 1)
    return {
        'last_updated': datetime.fromtimestamp(int(timestamp)),
        'last_author': author,
    }


def get_self_latest_commit_info():
    last_updated = subprocess.check_output(['git', 'log', '-1', '--format=%ai'], text=True, errors='ignore').strip()
    return {
        'last_updated': last_updated,
    }


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
                print('remove: {}'.format(target_file_path))
                os.remove(target_file_path)
    # 空ディレクトリの削除
    for root, dirs, files in os.walk(settings.OUTPUT_DIR, topdown=False):
        if '/.git' in root:
            continue

        if len(files) == 0:
            try:
                os.rmdir(root)
                print('remove directory: {}'.format(root))
            except Exception:
                pass


def convert_pageinfo(pageinfo, sidebar, sidebar_index, template, hrefs, global_qualify_list):
    path = pageinfo['path']
    if path.count("/") <= 1:
        print(path)

    latest_commit_info = get_latest_commit_info(pageinfo['path'])

    if not settings.DISABLE_SIDEBAR:
        sidebar.set_active(pageinfo['paths'])

    content_header = ContentHeader(pageinfo['paths'], sidebar, sidebar_index)
    context = {
        'title': (
            pageinfo['title'] if pageinfo['is_index'] else
            pageinfo['title'] + settings.TITLE_SUFFIX),
        'url': settings.BASE_URL + pageinfo['href'],
        'description': pageinfo['description'],
        'cachebust': _CACHEBUST,
        'disable_sidebar': settings.DISABLE_SIDEBAR,
        'sidebar': sidebar,
        'content_header': content_header,
        'brand': settings.BRAND,
        'search': settings.GOOGLE_SITE_SEARCH,
        'analytics': settings.GOOGLE_ANALYTICS,
        'rss': settings.BASE_URL + '/' + settings.RSS_PATH,
        'edit_url': settings.EDIT_URL_FORMAT.format(path=pageinfo['path'] + '.md'),
        'history_url': settings.HISTORY_URL_FORMAT.format(path=pageinfo['path'] + '.md'),
        'project_url': settings.PROJECT_URL,
        'project_name': settings.PROJECT_NAME,
        'latest_commit_info': latest_commit_info,
        'keywords': settings.META_KEYWORDS,
        'relative_base': ''
    }
    if settings.USE_RELATIVE_LINK:
        url_current_dir = posixpath.dirname(context['url'])
        context['relative_base'] = posixpath.relpath(settings.BASE_URL, url_current_dir)
        # 以下は <meta /> で埋め込む情報なので敢えて相対パスにはしない。
        # context['url'] = posixpath.relpath(context['url'], url_current_dir)
        # context['rss'] = posixpath.relpath(context['rss'], url_current_dir)
    convert(pageinfo['path'], template, context, hrefs, global_qualify_list)


def main():
    pageinfos = [make_pageinfo(path) for path in target_paths()]
    sidebar = make_sidebar(pageinfos)
    if 'index' in sidebar._children:
        sidebar_index = sidebar._children['index']
        del sidebar._children['index']
    else:
        sidebar_index = None

    with open('{}/GLOBAL_QUALIFY_LIST.txt'.format(settings.INPUT_DIR), encoding='utf-8') as f:
        global_qualify_list = '\n'.join([line.strip() for line in f])

    cache = Cache(CACHE_FILE)
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(settings.PAGE_TEMPLATE_DIR))
    template = env.get_template('content.html')
    hrefs = {pageinfo['href'] for pageinfo in pageinfos}

    target_pageinfos = []
    for pageinfo in pageinfos:
        if not pageinfo['path'].startswith(TARGET_PREFIX):
            continue
        required = cache.convert_required(pageinfo['path'])
        if not CONVERT_ALL and not required:
            # print(pageinfo['path'] + ' -- already converted')
            continue
        target_pageinfos.append(pageinfo)

    if settings.DISABLE_SIDEBAR:
        def run(pageinfos):
            for pageinfo in pageinfos:
                convert_pageinfo(pageinfo, sidebar, sidebar_index, template, hrefs, global_qualify_list)

        target_pageinfos_list = [[] for n in range(CONCURRENCY)]
        for i, pageinfo in enumerate(target_pageinfos):
            target_pageinfos_list[i % CONCURRENCY].append(pageinfo)

        import multiprocessing
        processes = []
        for i in range(CONCURRENCY):
            process = multiprocessing.Process(target=run, args=(target_pageinfos_list[i],))
            process.start()
            processes.append(process)
        for process in processes:
            process.join()
        for process in processes:
            if process.exitcode != 0:
                sys.exit(process.exitcode)

    else:
        # サイドバーを出力する場合は sidebar への書き込みが発生して怖いので普通に出力する
        for pageinfo in target_pageinfos:
            convert_pageinfo(pageinfo, sidebar, sidebar_index, template, hrefs, global_qualify_list)

    for pageinfo in pageinfos:
        cache.converted(pageinfo['path'])
    cache.flush()
    remove_not_target_paths(pageinfo['path'] for pageinfo in pageinfos)

    with open(os.path.join(settings.OUTPUT_DIR, settings.RSS_PATH), 'w', encoding='utf-8') as f:
        f.write(make_atom())

    with open(os.path.join(settings.OUTPUT_DIR, settings.SITEMAP_PATH), 'w', encoding='utf-8') as f:
        f.write(make_sitemap(pageinfos))

    # 静的ファイルをコピーする
    subprocess.call(['cp', '-v', '-RL'] + glob.glob(os.path.join(settings.STATIC_DIR, '*')) + [settings.OUTPUT_DIR])


if __name__ == '__main__':
    main()
