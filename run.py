#!/usr/bin/env python
#coding: utf-8
import os
import re
import markdown
import sys
import importlib
from collections import defaultdict

if len(sys.argv) != 2:
    print '{} <setting>'.format(sys.argv[0])
    sys.exit(0)

settings = importlib.import_module(sys.argv[1])


def convert(path, tmpl):
    md_data = open(os.path.join(settings.INPUT_DIR, path + '.md')).read()
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
    html_data = md.convert(unicode(md_data, encoding='utf-8'))

    dst_dir = os.path.dirname(os.path.join(settings.OUTPUT_DIR, path))
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
    open(os.path.join(settings.OUTPUT_DIR, path + '.html'), 'w').write(tmpl.replace('@@body@@', html_data.encode('utf-8')))


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
    filename = paths[-1]
    dirnames = paths[:-1]
    return {
        'path': path,
        'href': '/' + path + '.html',
        'title': title,
        'dirnames': dirnames,
        'filename': filename,
    }


def make_sidebar(pageinfos):
    # TODO: use template engine
    def quote(text):
        text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        return text

    link2_fmt = '''<li class="list-group-item"><a href="{href}">{title}</a></li>'''
    link1_fmt = '''
      <div class="panel panel-default">
        <div class="panel-heading" role="tab" id="{heading_id}">
          <h4 class="panel-title">
            <a data-toggle="collapse" data-parent="#accordion" href="#{collapse_id}" aria-expanded="true" aria-controls="{collapse_id}">
              {title}
            </a>
          </h4>
        </div>
        <div id="{collapse_id}" class="panel-collapse collapse" role="tabpanel" aria-labelledby="{heading_id}">
          <div class="panel-body">
            <h4 class="panel-title">
              <a href="{href}">
                {title}
              </a>
            </h4>
          </div>
          <ul class="list-group">
            {link2}
          </ul>
        </div>
      </div>
    '''
    html = '''<div class="panel-group" id="accordion" role="tablist" aria-multiselectable="true">{link1}</div>'''

    infodic = defaultdict(dict)
    for pageinfo in pageinfos:
        depth = len(pageinfo['dirnames'])
        if depth == 0:
            filename = pageinfo['filename']
            infodic[filename]['pageinfo'] = pageinfo
        if depth == 1:
            filename = pageinfo['dirnames'][0]
            if 'children' not in infodic[filename]:
                infodic[filename]['children'] = []
            infodic[filename]['children'].append(pageinfo)

    link1 = ''
    for filename in sorted(infodic):
        if 'children' not in infodic[filename]:
            continue
        if 'pageinfo' not in infodic[filename]:
            continue

        pageinfo = infodic[filename]['pageinfo']
        children = infodic[filename]['children']
        link2 = ''
        for child in children:
            link2 += link2_fmt.format(href=child['href'], title=quote(child['title']))
        heading_id = 'heading-' + pageinfo['path'].replace('/', '-')
        collapse_id = 'collapse-' + pageinfo['path'].replace('/', '-')
        link1 += link1_fmt.format(
            link2=link2,
            href=pageinfo['href'],
            title=quote(pageinfo['title']),
            heading_id=heading_id,
            collapse_id=collapse_id)

    return html.format(link1=link1)
    #return '<ul>{}</ul>'.format(
    #    ''.join(['<li><a href="{href}">{title}</a></li>'.format(**pageinfo) for pageinfo in pageinfos if len(pageinfo['dirnames']) < 2]))


def main():
    pageinfos = [make_pageinfo(path) for path in target_paths()]
    sidebar = make_sidebar(pageinfos)
    tmpl = open(settings.PAGE_TEMPLATE).read()
    tmpl = tmpl.replace('@@sidebar@@', sidebar)
    for pageinfo in pageinfos:
        print(pageinfo['path'])
        convert(pageinfo['path'], tmpl.replace('@@title@@', pageinfo['title']))


if __name__ == '__main__':
    main()
