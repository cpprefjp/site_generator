# -*- coding: utf-8 -*-
"""定義語をリンクに変換
=======================

DEFINED_WORDS.json でリンクの指定されている定義語を本文中から検索しリンクに変換
する。


xml.etree.ElementTree にまつわる実装の留意事項
----------------------------------------------

markdown.treeprocessors では Python の "標準的な XML ライブラリ"である
xml.etree.ElementTree (etree) を使っているようだ (最終的にこの実装では
markdown.postprocessors を用いることにしたので必ずしも xml.etree.ElementTree を
使わなければならないわけではないが)。etree のドキュメントはあるが仕様が色々信じ
がたいので結局直接ソースコード [1] を見るのが確実である。

* etree は XPath を部分的に実装していると謳っている [2] が XPath 特有の機能は全
  く実装されていない。子・子孫・属性による要素の選択を XPath に似た文法で指定で
  きるというだけである。XPath ならではの機能はない。textノードも抜き出せないし、
  何なら /xxx() のような文法はないし、集合演算にも対応していない。当初、以下を
  動かそうと試行錯誤していたが全く無駄な努力だった。

  for text in root.findall("(.//* except .//*/(a | code | pre)/*)/child::text()"):
    print(text)

* etree では要素からその親要素を取得する方法がない。なのでそもそも XPath なり何
  なりのセレクターで列挙したとしても自身を置き換えるような DOM 修正が不可能であ
  る。なので、木構造を直接自前で辿るしかない。

* etree の実装は不思議なことに node の概念がなく、文字列は直前の開始タグまたは
  終了タグの付属物として記録されている。element.text が開始タグ直後の文字列で
  element.tail が終了タグ直後の文字列である。特に、element.text は「その要素内
  に含まれる文字列全て」ではなく最初の子要素が現れるまでの文字列であるという事
  に注意する。親要素の最初の node としての文字列でないものは全て直前の要素の終
  了タグの付属物として記録されている。例えば、

    <a>text1<b>text2</b>text3<c>text4</c>text5</a>

  に対しては

    a.text = "text1"
    b.text = "text2"
    b.tail = "text3"
    c.text = "text4"
    c.tail = "text5"
    a.tail = None

  という具合に文字列が格納されている。

  元ソースの実体参照 ("&lt;" など) は解決された状態 (つまり "<" など) で tail,
  text に格納されると思われる。少なくとも a.text = "<"としたらソースに変換する
  時点で "&lt;" が出力される。

* 子要素を iterate する方法が分からないと思ったら親要素が Iterable であり
  elem.iter() で子要素のイテレータが得られる。これは変だ。

  for e in elem:
    print(e)

* etree では子要素を追加する elem.insert(index, childElement) という関数がある。
  引数に index を要求しているが、そもそも子要素を index 指定で取得する機能もな
  いし、子要素から index を取得する機能もないので、index の指定のしようがない。
  呼び出し側で、親要素の構築時に何番目にどの要素が格納されているかを別に記録し
  ていなければどうにもならない。或いは既存の要素に対して処理する時は elem を一
  旦 iterate して対応表を手元に作るか、private メンバ _children に直接アクセス
  する必要がある (但し _children はバージョンが変わった時に変わらないとも限らな
  い)。

* xml.dom.minidom という多少はましなものもある [3,4] 様だが xml.etree とは互換
  性がない。木を再構築する必要がある。これを使うのだったらそもそも
  markdown.treeprocessors を使う意味がない (現在は Postprocessor に移行して自前
  で xml.etree の木を構築しているのでこの際 minidom に乗り換えても良いのかもし
  れない)。

* Q 要素を作る時は必ず elem.SubElement などの関数経由で構築する必要はあるか?

  A. 恐らくない。直接要素を構築してから追加すれば良いと思われる。質問サイトの
  [5] の質疑応答を見る限りは ([5] の質問自体は今回の疑問と直接関係ないが)、取り
  合えず要素は etree.Element で作成してから append して問題ないようだ (DOM の場
  合には、アロケータの都合だろうか、document.createElement を使う必要があったが
  その様な制約はないようである)。

* etree では if elem: は elem に子要素が存在するかどうかで判定される。つまり、
  None かそうでないかの判定に使おうと思っていると痛い目を見る。

- [1] https://github.com/python/cpython/blob/main/Lib/xml/etree/ElementTree.py
- [2] https://docs.python.org/ja/3/library/xml.etree.elementtree.html#elementtree-xpath
- [3] [XMLを扱うモジュール群 — Python 3.10.4 ドキュメント](https://docs.python.org/ja/3/library/xml.html)
- [4] https://github.com/python/cpython/blob/main/Lib/xml/dom/minidom.py
- [5] https://stackoverflow.com/questions/37572695/python-etree-insert-append-and-subelement


その他の留意事項
----------------

* Python-Markdown のプロセッサの処理順序: md.treeprocessors.register,
  md.postprocessors.register の第3引数 priority に渡す値で処理の順序が変わる。
  小さな値の方が後段で処理が実施されるようだ。postprocessors の場合 10 より小さ
  な値を指定しておけば最後に実施される。

  treeprocessors の場合、priority=1 に設定すると:

  * リンク []() は要素 a に変換された状態で渡されるので問題なくスキップできる。

  * 実体参照は "乱数:番号" に置換された状態で渡される。つまり、<>& などを含んだ
    文字列に対して一致させることはできない?

  * htmlStash されている要素はこの時点で "乱数:番号" に変換されているので、中に
    含まれる単語について処理することはできない。

  実体参照や htmlStash された文字列は Postprocessor で復元される。
  Python-Markdown のソースを見ると Treeprocessors を全て処理した後に
  Postprocessor が実行されるので、実体参照や htmlStash された情報を参照する処理
  は Treeprocessor ではできない。仕方がないので Postprocessor で処理することに
  した。

"""

from markdown.extensions import Extension
from markdown.postprocessors import Postprocessor

import regex as re

import xml.etree.ElementTree as etree

# リンク・コード・タイトルなどの内部は自動リンクの対象としない。除外タグ判定用正規表現
_RE_EXCLUDED_TAGS = re.compile(r'^(?:a|code|pre|kbd|dfn|h1)$', re.IGNORECASE)

# 自動リンク対象を英単語境界に一致させる必要があるかの判定用正規表現
_RE_WBEG = re.compile(r'^[\p{Ll}\p{Lu}_0-9]')
_RE_WEND = re.compile(r'[\p{Ll}\p{Lu}_0-9]$')

# ソース名 (.md) からHTML名 (.html) に置換する時に使う正規表現
_RE_LINK_EXTENSION = re.compile(r'^([^?#]+?)(?:\.md)([?#]|$)')

# リンクに "https:" 等のスキーム名が含まれているか判定するのに使う正規表現
_RE_LINK_SCHEME = re.compile(r'^[a-zA-Z0-9]+:')


def _quoteWordForRegex(word):
    ret = re.escape(word)
    if _RE_WBEG.match(word):
        ret = r'(?<=^|[^\p{Ll}\p{Lu}_0-9])' + ret
    if _RE_WEND.search(word):
        ret = ret + r'(?=$|[^\p{Ll}\p{Lu}_0-9])'
    return ret


class DefinedWordTreeprocessor(Postprocessor):
    """A postprocessor for Python-Markdown to create links of defined words."""

    def _resolveWordProperty(self, word, prop):
        if prop in self._dict[word]:
            return self._dict[word][prop], None
        visited = {}
        while 'redirect' in self._dict[word]:
            if word in visited:
                raise Exception("defined_words: redirection loop for '%s'" % word)
            visited[word] = True
            word = self._dict[word]['redirect']
            if prop in self._dict[word]:
                return self._dict[word][prop], word
        return None, None

    def _resolveDictionary(self):
        for word in self._dict.keys():
            entry = self._dict[word]
            if 'link' not in entry:
                value, redirect = self._resolveWordProperty(word, 'link')
                if value is not None:
                    entry['link'] = value
            if 'desc' not in entry:
                value, redirect = self._resolveWordProperty(word, 'desc')
                if value is not None:
                    entry['desc'] = "%s。%s" % (redirect, value)

        for word in self._dict.keys():
            entry = self._dict[word]
            if 'link' in entry:
                link = entry['link']
                if _RE_LINK_SCHEME.search(link) is None:
                    link = _RE_LINK_EXTENSION.sub(r'\1%s\2' % self.extension, link, count=1)
                    if not link.startswith('/'):
                        raise Exception("defined_words: link='%s': relative link is unallowed" % link)
                    link = self.base_url + link
                entry['resolved_link'] = link

    def __init__(self, md, config):
        Postprocessor.__init__(self, md)
        self._markdown = md

        self.config = config
        self.base_url = self.config['base_url']
        self.base_path = self.config['base_path']
        self.extension = self.config['extension']
        self._dict = self.config['dict']

        if len(self._dict) > 0:
            # Note: regex には 500 個の制限があるらしい (以下参照)。
            # https://github.com/cpprefjp/site_generator/issues/72
            # https://github.com/cpprefjp/markdown_to_html/commit/fb18c87b48c6290dd6ba00141ecb2f5dc8aba930
            if len(self._dict) > 500:
                raise Exception("Too many defined words: count = %d must not be greater than 500" % len(self._dict))
            # Note: できるだけ長い一致を優先させるため逆ソートしてから正規表現にす
            # る。例えば "不定|不定値" ではなく "不定値|不定" になるようにしないと、
            # 本文中の "不定値" に対して "[不定値]" とリンク付けされて欲しいが "[不
            # 定]値" とリンク付けされてしまう。
            self.re_defined_words = re.compile(r'|'.join([_quoteWordForRegex(key) for key in sorted(self._dict.keys(), reverse=True)]), re.MULTILINE)

            self._resolveDictionary()

    def _convertText(self, text):
        new_text = None
        ins = []
        pos = 0
        prev = None
        for m in self.re_defined_words.finditer(text):
            word = m.group(0)
            if word not in self._dict:
                continue
            left = text[pos:m.start()]
            if prev is not None:
                prev.tail = left
            else:
                new_text = left

            entry = self._dict[word]
            attrs = {'class': 'cpprefjp-defined-word'}
            if 'resolved_link' in entry:
                attrs['href'] = entry['resolved_link']
            if 'desc' in entry:
                attrs['data-desc'] = entry['desc']
            a = etree.Element('a', attrs)
            a.text = word
            ins.append(a)

            pos = m.end()
            prev = a

        left = text[pos:]
        if prev is not None:
            prev.tail = left
        else:
            new_text = left

        return new_text, ins

    def _recurseElement(self, elem):
        if elem.tag is etree.Comment or elem.tag is etree.ProcessingInstruction:
            return
        if _RE_EXCLUDED_TAGS.match(elem.tag):
            return

        insertions = []

        if elem.text is not None:
            elem.text, ins = self._convertText(elem.text)
        else:
            ins = []
        insertions.append(ins)

        for e in elem:
            self._recurseElement(e)
            if e.tail is not None:
                e.tail, ins = self._convertText(e.tail)
            else:
                ins = []
            insertions.append(ins)

        for i, ins in reversed(list(enumerate(insertions))):
            for e in reversed(ins):
                elem.insert(i, e)

    def run(self, text):
        """Construct ElementTree, convert and re-serialize it"""
        if len(self._dict) == 0:
            return

        try:
            md = self._markdown
            text = '<{tag}>{text}</{tag}>'.format(tag=md.doc_tag, text=text)
            root = etree.fromstring(text)
            self._recurseElement(root)
            output = etree.tostring(root, encoding="unicode", method="xml")
            beg = output.index('<%s>' % md.doc_tag) + len(md.doc_tag) + 2
            end = output.rindex('</%s>' % md.doc_tag)
            return output[beg:end].strip()
        except etree.ParseError as e:
            lineno = e.position[0]
            xs = text.split('\n')[lineno - 5:lineno + 5]
            print('[Parse Error : {0}]'.format(self.config['full_path']))
            for x, n in zip(xs, range(lineno - 5, lineno + 5)):
                print('{0:5d} {1}'.format(n + 1, x))
            raise


class DefinedWordExtension(Extension):
    """An extension for Python-Markdown to create links of defined words."""

    def __init__(self, **kwargs):
        # define default configs
        self.config = {
            'base_url': ["https://cpprefjp.github.io",
                         "base url of the site"],
            'base_path': ["",
                          "directory path that contains the current document"],
            'full_path': ["implementation-compliance.md",
                          "path to the source file"],
            'extension': ['.html',
                          "the extension of the generated HTML files"],
            'dict': [{"不適格": "/implementation-compliance.md"},
                     "dictionary that maps a defined word to a link"],
        }

        for key, value in kwargs.items():
            if key in self.config:
                self.setConfig(key, value)

    def extendMarkdown(self, md):
        """Add DefinedWordTreeprocessor to Markdown instance."""
        proc = DefinedWordTreeprocessor(md, self.getConfigs())
        md.postprocessors.register(proc, 'defined_words', 1)
        md.registerExtension(self)


def makeExtension(**kwargs):
    return DefinedWordExtension(**kwargs)
