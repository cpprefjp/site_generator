# -*- coding: utf-8 -*-
"""
Fenced Code Extension の改造版
=========================================

github でのコードブロック記法が使える。

    >>> text = '''
    ... `````
    ... # コードをここに書く
    ... x = 10
    ... `````'''
    >>> print markdown.markdown(text, extensions=['qualified_fenced_code'])
    <pre><code># コードをここに書く
    x = 10
    </code></pre>

かつ、これらのコードに修飾ができる。

    >>> text = '''
    ... ```
    ... x = [3, 2, 1]
    ... y = sorted(x)
    ... x.sort()
    ... ```
    ... sorted[color ff0000]
    ... sort[link http://example.com/]
    ... '''
    >>> print markdown.markdown(text, extensions=['qualified_fenced_code'])
"""

import hashlib

import regex as re

from markdown.extensions.codehilite import CodeHilite
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor

CODE_WRAP = '<pre><code%s>%s</code></pre>'
LANG_TAG = ' class="%s"'

# qualifier の各行は以下の形式を持つことを要求する。"*" による箇条書きの項目で
# あり、[meta ...], [mathjax enable ...], [link ...], [color ...], [italic] の
# 何れかの修飾子が含まれていること。インデントレベルは少なくとも閉じ ``` と同じ
# であること。
QUALIFIER_LINE_RE_STRING = r'(?P=indent)\s*\*\s[^\n]*\[(?:meta|mathjax enable|link|color|italic)\b[^\n]*\][^\n]*\n'

# 以下の正規表現は qualifier 行の連続を規定する。最初の qualifier が、閉じ ```
# と同じレベルの "*" による箇条書きの項目でなければそこで中断する。
QUALIFIERS_RE_STRING = r'(?:(?!(?P=indent)\*\s)|(?P<qualifies>(?:%s)*))' % QUALIFIER_LINE_RE_STRING

QUALIFIED_FENCED_BLOCK_RE = re.compile(r'(?P<fence>`{3,})[ ]*(?P<lang>[a-zA-Z0-9_+-]*)(?P<lang_meta>.*?)\n(?P<code>.*?)(?<=\n)(?P<indent>[ \t]*)(?P=fence)[ ]*\n' + QUALIFIERS_RE_STRING, re.MULTILINE | re.DOTALL)
QUALIFY_COMMAND_RE = re.compile(r'\[(.*?)\]')
INDENT_RE = re.compile(r'^[ \t]+', re.MULTILINE)


class QualifiedFencedCodeExtension(Extension):

    def __init__(self, global_qualify_list):
        self.global_qualify_list = global_qualify_list

    def extendMarkdown(self, md):
        fenced_block = QualifiedFencedBlockPreprocessor(md, self.global_qualify_list)
        md.registerExtension(self)

        md.preprocessors.register(fenced_block, 'qualified_fenced_code', 29)


def _make_random_string():
    """アルファベットから成るランダムな文字列を作る"""
    from random import randrange
    import string
    alphabets = string.ascii_letters
    return ''.join(alphabets[randrange(len(alphabets))] for i in range(32))


def _escape(txt):
    """basic html escaping"""
    txt = txt.replace('&', '&amp;')
    txt = txt.replace('<', '&lt;')
    txt = txt.replace('>', '&gt;')
    txt = txt.replace('"', '&quot;')
    return txt


class QualifyDictionary(object):

    def __init__(self):
        # 各コマンドに対する実際の処理
        def _qualify_italic(*xs):
            return '<i>{0}</i>'.format(*xs)

        def _qualify_color(*xs):
            return '<span style="color:#{1}">{0}</span>'.format(*xs)

        def _qualify_link(*xs):
            return '<a href="{1}">{0}</a>'.format(*xs)

        self.qualify_dic = {
            'italic': _qualify_italic,
            'color': _qualify_color,
            'link': _qualify_link,
        }


class Qualifier(object):

    """修飾１個分のデータを保持するクラス"""

    def __init__(self, line, qdic):
        command_res = [r'(\[{cmd}(\]|.*?\]))'.format(cmd=cmd) for cmd in qdic.qualify_dic]

        qualify_re_str = r'^[ \t]*\*[ \t]+(?P<target>.*?)(?P<commands>({commands})+)$'.format(
            commands='|'.join(command_res))
        qualify_re = re.compile(qualify_re_str)

        # parsing
        m = qualify_re.search(line)
        if not m:
            raise ValueError('Failed parse')
        self.target = m.group('target')
        self.commands = []

        def f(match):
            self.commands.append(match.group(1))

        try:
            QUALIFY_COMMAND_RE.sub(f, m.group('commands'))
        except TypeError:
            # workaround for regex library
            # TypeError: expected string instance, NoneType found
            pass

        self._target_re = None
        self._target_re_text = None

    # 置換対象になる単語を正規表現で表す
    def get_target_re_text(self):
        if self._target_re_text is None:
            target_re_text = '((?<=[^a-zA-Z_])|(?:^)){target}((?=[^a-zA-Z_])|(?:$))'.format(target=re.escape(self.target))
            self._target_re_text = '(?:{})'.format(target_re_text)
        return self._target_re_text

    def _get_target_re(self):
        if self._target_re is None:
            target_re = re.compile(self.get_target_re_text())
            self._target_re = target_re
        return self._target_re

    def find_match(self, code):
        return self._get_target_re().search(code) is not None


class QualifierList(object):

    def __init__(self, lines):
        self._qdic = QualifyDictionary()

        # Qualifier を作るが、エラーになったデータは取り除く
        def unique(xs):
            seen = set()
            results = []
            for x in xs:
                if x not in seen:
                    seen.add(x)
                    try:
                        results.append(Qualifier(x, self._qdic))
                    except Exception:
                        pass
            return results

        self._qs = unique(lines)

    def mark(self, code):
        """置換対象になる単語にマーキングを施す

        対象文字列が 'sort' だとすれば、文字列中にある全ての 'sort' を
        '{ランダムな文字列}'
        という文字列に置換する。
        """
        if len(self._qs) == 0:
            self._code_re = re.compile("")
            return code

        pre_target_re_text_list = [q.get_target_re_text() for q in self._qs if q.find_match(code)]
        if len(pre_target_re_text_list) == 0:
            self._code_re = re.compile("")
            return code

        target_re_text = '|'.join(pre_target_re_text_list)

        # 対象となる単語を置換し、その置換された文字列を後で辿るための正規表現（text_re_list）と、
        # 置換された文字列に対してどのような修飾を行えばいいかという辞書（match_qualifier）を作る。
        text_re_list = []
        match_qualifier = {}

        def mark_command(match):
            # 各置換毎に一意な文字列を用意する
            match_name = _make_random_string()
            # 対象となる単語がどの修飾のデータなのかを調べる
            text = match.group(0)
            q = next(q for q in self._qs if q.target == text)
            match_qualifier[match_name] = q

            # text をこの文字列に置換する
            text = '{match_name}'.format(
                match_name=match_name,
            )
            # 置換された text だけを確実に検索するための正規表現
            text_re = '(?P<{match_name}>{match_name})'.format(
                match_name=match_name
            )
            text_re_list.append(text_re)
            return text
        # 対象になる単語を一括置換
        code = re.sub(target_re_text, mark_command, code)
        # マークされた文字列を見つけるための正規表現を作る
        self._code_re = re.compile('|'.join(r for r in text_re_list))
        self._match_qualifier = match_qualifier
        return code

    def qualify(self, html):
        # 修飾の指定がなかった
        if len(self._qs) == 0:
            return html
        # 修飾の指定はあったが、検索してみると修飾する文字列が見つからなかった
        if len(self._code_re.pattern) == 0:
            return html

        # マークされた文字列を探しだして、そのマークに対応した修飾を行う
        def convert(match):
            q = next(q for m, q in self._match_qualifier.items() if match.group(m))
            text = _escape(q.target)
            for command in q.commands:
                xs = command.split(' ')
                c = xs[0]
                remain = xs[1:]
                # 修飾
                text = self._qdic.qualify_dic[c](text, *remain)
            return text
        return self._code_re.sub(convert, html)


def _removeIndent(code, indent):
    if len(indent) == 0:
        return code
    n = len(indent.expandtabs(4))
    return INDENT_RE.sub(lambda m: m.group().expandtabs(4)[n:], code)


class QualifiedFencedBlockPreprocessor(Preprocessor):

    def __init__(self, md, global_qualify_list):
        Preprocessor.__init__(self, md)

        md._example_codes = []
        self.checked_for_codehilite = False
        self.codehilite_conf = {}
        self.global_qualify_list = global_qualify_list

    def run(self, lines):
        # Check for code hilite extension
        if not self.checked_for_codehilite:
            for ext in self.md.registeredExtensions:
                if isinstance(ext, CodeHiliteExtension):
                    self.codehilite_conf = ext.config
                    break

            self.checked_for_codehilite = True

        text = "\n".join(lines)

        example_counter = 0

        while 1:
            m = QUALIFIED_FENCED_BLOCK_RE.search(text)
            if m:
                # ```cpp example みたいに書かれていたらサンプルコードとして扱う
                is_example = m.group('lang_meta') and ('example' in m.group('lang_meta').strip().split())

                qualifies = m.group('qualifies') or ''
                qualifies = qualifies + self.global_qualify_list
                qualifies = [f for f in qualifies.split('\n') if f]
                code = _removeIndent(*m.group('code', 'indent'))

                # サンプルコードだったら、self.markdown の中にコードの情報と ID を入れておく
                if is_example:
                    example_id = hashlib.sha1((str(example_counter) + code).encode('utf-8')).hexdigest()
                    self.md._example_codes.append({"id": example_id, "code": code})
                    example_counter += 1

                qualifier_list = QualifierList(qualifies)
                code = qualifier_list.mark(code)

                # If config is not empty, then the codehighlite extension
                # is enabled, so we call it to highlite the code
                if self.codehilite_conf and m.group('lang'):
                    highliter = CodeHilite(
                        code,
                        linenums=self.codehilite_conf['linenums'][0],
                        guess_lang=self.codehilite_conf['guess_lang'][0],
                        css_class=self.codehilite_conf['css_class'][0],
                        style=self.codehilite_conf['pygments_style'][0],
                        lang=(m.group('lang') or None),
                        noclasses=self.codehilite_conf['noclasses'][0])

                    code = highliter.hilite()
                    # サンプルコードだったら <div id="..." class="yata"> で囲む
                    if is_example:
                        code = '<div id="%s" class="yata">%s</div>' % (example_id, code)
                else:
                    lang = ''
                    if m.group('lang'):
                        lang = LANG_TAG % m.group('lang')

                    code = CODE_WRAP % (lang, _escape(code))

                code = qualifier_list.qualify(code)

                placeholder = self.md.htmlStash.store(code)
                text = '%s\n%s\n%s' % (text[:m.start()], placeholder, text[m.end():])
            else:
                break
        return text.split("\n")


def makeExtension(**kwargs):
    return QualifiedFencedCodeExtension(**kwargs)
