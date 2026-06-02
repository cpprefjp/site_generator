# -*- coding: utf-8 -*-
"""
markdown から変換した HTML に属性を追加する
"""

import posixpath
import re
import sys

import markdown
from markdown import postprocessors
from markdown import serializers

import xml.etree.ElementTree as etree

HTML_TAGS = {
    'a',
    'abbr',
    'address',
    'area',
    'article',
    'aside',
    'audio',
    'b',
    'base',
    'bdi',
    'bdo',
    'blockquote',
    'body',
    'br',
    'button',
    'canvas',
    'caption',
    'cite',
    'code',
    'col',
    'colgroup',
    'command',
    'datalist',
    'dd',
    'del',
    'details',
    'dfn',
    'div',
    'dl',
    'dt',
    'em',
    'embed',
    'fieldset',
    'figcaption',
    'figure',
    'footer',
    'form',
    'h1',
    'h2',
    'h3',
    'h4',
    'h5',
    'h6',
    'head',
    'header',
    'hgroup',
    'hr',
    'html',
    'i',
    'iframe',
    'img',
    'input',
    'ins',
    'kbd',
    'keygen',
    'label',
    'legend',
    'li',
    'link',
    'map',
    'mark',
    'menu',
    'meta',
    'meter',
    'nav',
    'noscript',
    'object',
    'ol',
    'optgroup',
    'option',
    'output',
    'p',
    'param',
    'pre',
    'progress',
    'q',
    'rp',
    'rt',
    'ruby',
    's',
    'samp',
    'script',
    'section',
    'select',
    'small',
    'source',
    'span',
    'strong',
    'style',
    'sub',
    'summary',
    'sup',
    'table',
    'tbody',
    'td',
    'textarea',
    'tfoot',
    'th',
    'thead',
    'time',
    'title',
    'tr',
    'track',
    'u',
    'ul',
    'var',
    'video',
    'wbr',
}


class SafeRawHtmlPostprocessor(postprocessors.Postprocessor):

    HTML_TAG_RE = re.compile(r'^\<\/?([a-zA-Z0-9]+)[^\>]*\>$')

    def run(self, text):
        for i in range(self.markdown.htmlStash.html_counter):
            html = self.markdown.htmlStash.rawHtmlBlocks[i]
            # if not safe:
            #     html = self.escape(html)
            text = text.replace(self.markdown.htmlStash.get_placeholder(i), html)
        return text

    def escape(self, html):
        # html tag
        m = re.match(self.HTML_TAG_RE, html)
        if m:
            if m.group(1) in HTML_TAGS:
                return html
        # html entity
        m = re.match(r'^\&.*\;$', html)
        if m:
            return html
        return self.basic_escape(html)

    def basic_escape(self, html):
        html = html.replace('&', '&amp;')
        html = html.replace('<', '&lt;')
        html = html.replace('>', '&gt;')
        return html.replace('"', '&quot;')


class AttributePostprocessor(postprocessors.Postprocessor):

    def __init__(self, md, config):
        postprocessors.Postprocessor.__init__(self, md)
        self._markdown = md

        self.config = config
        self.re_url_hash = re.compile(r'#.*$')
        self.url_base = self.config['base_url'].strip('/') + '/'
        self.url_current = self.url_base + self._remove_md(self.config['full_path'])
        self.url_current_base = self.url_base + self.config['base_path'].strip('/')

        image_repo = self.config['image_repo']
        self.re_url_github_image = re.compile(r'^https?://(?:raw.github.com/%s/master|github.com/%s/raw)/' % (image_repo, image_repo))
        self.image_base = 'https://raw.githubusercontent.com/%s/master/' % image_repo

    def _iterate(self, elements, f):
        f(elements)
        for child in elements:
            self._iterate(child, f)

    def _add_color_code(self, element):
        if element.tag == 'code':
            text = element.text
            element.text = ''
            e = etree.SubElement(element, 'span', style='color: #000')
            e.text = text

    def _add_border_table(self, element):
        if element.tag == 'table':
            element.attrib['border'] = '1'
            element.attrib['bordercolor'] = '#888'
            element.attrib['style'] = 'border-collapse:collapse'

    def _remove_md(self, url):
        # サイト内絶対パスで末尾に .md があった場合、取り除く
        # （github のプレビューとの互換性のため）
        # その後、指定があればその拡張子を追加する
        matched = re.match('([^#]*)\\.md(#.*)?$', url)
        if matched:
            url = matched.group(1)
            if self.config['extension']:
                url = url + self.config['extension']
            anchor = matched.group(2)
            if anchor is not None:
                url = url + anchor
        return url

    def _to_absolute_url(self, element):
        if element.tag == 'a' and 'href' in element.attrib:
            base_url = self.config['base_url'].strip('/')
            base_paths = self.config['base_path'].strip('/').split('/')
            full_path = self.config['full_path']

            check_href = None

            url = element.attrib['href']
            if url.startswith('http://') or url.startswith('https://'):
                # 絶対パス
                base_url_body = base_url.split('//', 2)[1]
                url_body = url.split('//', 2)[1]
                # 別ドメインの場合は別タブで開く
                if not url_body.startswith(base_url_body):
                    element.attrib['target'] = '_blank'
                else:
                    check_href = url_body[len(base_url_body):]
            elif url.startswith('/'):
                # サイト内絶対パス
                element.attrib['href'] = base_url + url
                element.attrib['href'] = self._remove_md(element.attrib['href'])
                check_href = self._remove_md(url)
            elif url.startswith('#'):
                # ページ内リンク
                element.attrib['href'] = base_url + '/' + self._remove_md(full_path) + url
                check_href = '/' + self._remove_md(full_path)
            elif url.startswith('mailto:'):
                # メール
                pass
            else:
                # サイト内相対パス
                paths = []
                for p in base_paths + url.split('/'):
                    if p == '':
                        continue
                    elif p == '.':
                        continue
                    elif p == '..':
                        paths = paths[:-1]
                    else:
                        paths.append(p)
                element.attrib['href'] = base_url + '/' + '/'.join(paths)
                element.attrib['href'] = self._remove_md(element.attrib['href'])
                check_href = self._remove_md('/' + '/'.join(paths))

            if hasattr(self._markdown, '_html_attribute_hrefs') and self._markdown._html_attribute_hrefs is not None:
                # パスの存在チェック
                if check_href is not None:
                    check_href = re.sub('#.*', '', check_href)
                    if check_href.endswith('.nolink'):
                        # そのうち作られるはずだけど、まだリンク先のファイルが存在していないケース
                        if self._remove_md(check_href.replace('.nolink', '')) in self._markdown._html_attribute_hrefs:
                            # .nolink マークされていたけど、実際はもうこのファイルは作られているっぽいケース
                            # .nolink を外すこと
                            sys.stderr.write('Warning: [nolinked {full_path}] href "{url} ({check_href})" found.\n'.format(**locals()))
                            element.tag = 'span'
                        else:
                            # このファイルを作るように促す
                            check_href = check_href.replace('.nolink', '')
                            sys.stdout.write('Note: You can create {check_href} for {full_path}.\n'.format(**locals()))
                            element.tag = 'span'
                    else:
                        # .nolink でない、普通のファイル
                        if check_href not in self._markdown._html_attribute_hrefs:
                            sys.stderr.write('Warning: [{full_path}] href "{url} ({check_href})" not found.\n'.format(**locals()))
                            element.tag = 'span'

    def _to_relative_url(self, element):
        if element.tag == 'a' and 'href' in element.attrib:
            href = element.attrib['href']
            if self.re_url_hash.sub("", href) == self.url_current:
                element.attrib['href'] = href[len(self.url_current):]
            elif href.startswith(self.url_base):
                element.attrib['href'] = posixpath.relpath(href, self.url_current_base)

    def _resolve_image_src(self, element):
        if element.tag == 'img' and 'src' in element.attrib:
            src = element.attrib['src']
            src = self.re_url_github_image.sub(self.image_base, src, count=1)
            if self.config['use_static_image'] and src.startswith(self.image_base):
                src = 'static/image/' + src[len(self.image_base):]
                if self.config['use_relative_link']:
                    src = posixpath.relpath(self.url_base + src, self.url_current_base)
                else:
                    src = '/' + src
            element.attrib['src'] = src

    def _adjust_url(self, element):
        self._to_absolute_url(element)

        # 一旦絶対パスに統一してから相対パスに変換する
        if self.config['use_relative_link']:
            self._to_relative_url(element)

        self._resolve_image_src(element)

    def _add_meta(self, element):
        body = etree.Element('div', itemprop="articleBody")
        after_h1 = False
        for e in list(element):
            if e.tag == 'h1':
                e.attrib['itemprop'] = 'name'
                after_h1 = True
            elif after_h1:
                body.append(e)
                element.remove(e)
        element.append(body)

    def _tohtml(self, element):
        # Note: 以下の様に etree.tostring(method="xml") を用いると
        # <span></span> や <td></td> が <span /> や <td /> になってしまう。また、
        # HTML 属性の順序が保持されない。
        #
        # return etree.tostring(element, encoding="unicode", method="xml")

        # Note: 代わりに etree.tostring(method="html") を用いると、今度は <img
        # /> や <br /> が <img> や <br> になってしまい好ましくない。またこの時
        # も HTML 属性の順序が保持されない。
        #
        # return etree.tostring(element, encoding="unicode", method="html")

        # 今は代わりに以下のようにして markdown.serializers の内部変数
        # markdown.serializers.RE_AMP を一時的に書き換えることによって期待する
        # 動作を得ている。これは markdown.serializers の内部実装に依存している
        # ので、markdown.serializers の上流で内部実装に変更があると動かなくなる
        # 可能性があることに注意する。
        old_RE_AMP = serializers.RE_AMP
        try:
            serializers.RE_AMP = re.compile(r'&')
            output = self._markdown.serializer(element)
        finally:
            serializers.RE_AMP = old_RE_AMP
        return output

    def run(self, text):
        text = '<{tag}>{text}</{tag}>'.format(tag=self._markdown.doc_tag, text=text)
        try:
            root = etree.fromstring(text)
        except etree.ParseError as e:
            lineno = e.position[0]
            xs = text.split('\n')[lineno - 5:lineno + 5]
            print('[Parse Error : {0}]'.format(self.config['full_path']))
            for x, n in zip(xs, range(lineno - 5, lineno + 5)):
                print('{0:5d} {1}'.format(n + 1, x))
            raise
        # self._iterate(root, self._add_color_code)
        self._iterate(root, self._add_border_table)
        self._iterate(root, self._adjust_url)
        self._add_meta(root)

        output = self._tohtml(root)
        if self._markdown.stripTopLevelTags:
            try:
                start = output.index('<%s>' % self._markdown.doc_tag) + len(self._markdown.doc_tag) + 2
                end = output.rindex('</%s>' % self._markdown.doc_tag)
                output = output[start:end].strip()
            except ValueError:
                if output.strip().endswith('<%s />' % self._markdown.doc_tag):
                    # We have an empty document
                    output = ''
                else:
                    # We have a serious problem
                    raise ValueError('Markdown failed to strip top-level tags. Document=%r' % output.strip())
        return output


class AttributeExtension(markdown.Extension):

    def __init__(self, **kwargs):
        # デフォルトの設定
        self.config = {
            'base_url': ['', "Base URL used to link URL as absolute URL"],
            'base_path': ['', "Base Path used to link URL as relative URL"],
            'full_path': ['', "Full Path used to link URL as anchor URL"],
            'extension': ['', "URL extension"],
            'use_relative_link': [False, "Whether to use relative paths for domestic links"],
            'image_repo': ['cpprefjp/image', "Name of GitHub repository that contains the images"],
            'use_static_image': [False, "Whether to use the images in static/image instead on GitHub"]
        }

        super().__init__(**kwargs)

    def extendMarkdown(self, md):
        attr = AttributePostprocessor(md, self.getConfigs())
        md.postprocessors.register(attr, 'html_attribute', 0)
        md.postprocessors.deregister('raw_html')
        md.postprocessors.register(SafeRawHtmlPostprocessor(md), 'raw_html', 30)


def makeExtension(**kwargs):
    return AttributeExtension(**kwargs)
