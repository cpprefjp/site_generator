#coding: utf-8
import os
import re
import markdown

# 入力ディレクトリ
INPUT_DIR = 'site'

# 出力ディレクトリ
OUTPUT_DIR = 'cpprefjp.github.io'

# URL ベース
BASE_URL = 'http://cpprefjp.github.io'
EDIT_URL_FORMAT = 'https://github.com/cpprefjp/site/edit/master/{paths}'


def convert(path, tmpl):
    md_data = open(os.path.join(INPUT_DIR, path + '.md')).read()
    paths = path.split('/')

    qualified_fenced_code = 'markdown_to_html.qualified_fenced_code'
    html_attribute = 'markdown_to_html.html_attribute(base_url={base_url}, base_path={base_path}, full_path={full_path}, extension={extension})'.format(
        base_url=BASE_URL,
        base_path='/'.join(paths[:-1]),
        full_path=path + '.md',
        extension='.html',
    )
    # footer = 'markdown_to_html.footer(url={url})'.format(
    #     url=EDIT_URL_FORMAT.format(
    #         paths=path + '.md',
    #     )
    # )

    md = markdown.Markdown([
        'tables',
        qualified_fenced_code,
        'codehilite(noclasses=True)',
        html_attribute])
    html_data = md.convert(unicode(md_data, encoding='utf-8'))

    dst_dir = os.path.dirname(os.path.join(OUTPUT_DIR, path))
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
    open(os.path.join(OUTPUT_DIR, path + '.html'), 'w').write(tmpl.replace('@@body@@', html_data.encode('utf-8')))


def target_paths():
    for root, dirs, files in os.walk(INPUT_DIR):
        for f in files:
            if f.endswith('.md'):
                path = os.path.join(root, f)[len(INPUT_DIR):].lstrip('/')
                # 更新対象でないファイルは無視する
                if re.match('^([A-Z].*)|(.*!(\.md))$', path.split('/')[-1]):
                    continue
                # .md を取り除く
                path = path[:-3];
                yield path


def make_pageinfo(path):
    paths = path.split('/')
    title = paths[-1] # TODO
    filename = paths[-1]
    dirnames = paths[:-1]
    return {
        'path': path,
        'href': '/' + path + '.html',
        'title': title,
        'dirnames': dirnames,
        'filename': filename,
    }


def make_header(pageinfos):
    return '<ul>{}</ul>'.format(
        ''.join(['<li><a href="{href}">{title}</a></li>'.format(**pageinfo) for pageinfo in pageinfos if len(pageinfo['dirnames']) < 2]))


def main():
    pageinfos = [make_pageinfo(path) for path in target_paths()]
    header = make_header(pageinfos)
    tmpl = open('template.html').read()
    tmpl = tmpl.replace('@@header@@', header)
    for pageinfo in pageinfos:
        print(pageinfo['path'])
        convert(pageinfo['path'], tmpl.replace('@@title@@', pageinfo['title']))


if __name__ == '__main__':
    main()
