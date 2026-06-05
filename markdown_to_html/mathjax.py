# -*- coding: utf-8 -*-
"""
MathJax を使えるようにする
=========================

テキストのどこかに以下の文字列を書くことで有効になる

* [mathjax enable]

MathJaxを有効にした場合、$$...$$ （ブロック）か $...$ （インライン）に挟まれた文字列が数式になる
"""

import re

from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor
from markdown.util import code_escape


MATHJAX_CONFIG_RE = re.compile(r'^\s*\*\s*(?P<target>.*?)\[mathjax\s+(?P<name>.*?)\]\s*$')
MATHJAX_BLOCK_RE = re.compile(r'\$\$.*?\$\$', re.MULTILINE | re.DOTALL)
MATHJAX_INLINE_RE = re.compile(r'\$[^\\\$]*(?:\\\$[^\\\$]*)*\$')


class MathJaxExtension(Extension):

    def extendMarkdown(self, md):
        mathjaxpre = MathJaxPreprocessor(md)

        md.registerExtension(self)
        md.preprocessors.register(mathjaxpre, 'mathjax', 25)


class MathJaxPreprocessor(Preprocessor):

    def __init__(self, md):
        Preprocessor.__init__(self, md)
        self._markdown = md

    def run(self, lines):
        lines2 = []
        self._markdown._mathjax_enabled = False
        for line in lines:
            m = MATHJAX_CONFIG_RE.match(line)
            if m:
                name = m.group('name')
                if name == 'enable':
                    self._markdown._mathjax_enabled = True
            else:
                lines2.append(line)
        if not self._markdown._mathjax_enabled:
            return lines2

        text = "\n".join(lines2)
        while True:
            m = MATHJAX_BLOCK_RE.search(text)
            if not m:
                break
            tex = m.group(0)
            placeholder = self.md.htmlStash.store(code_escape(tex))
            text = text[:m.start()] + placeholder + text[m.end():]

        lines3 = []

        for line in text.split('\n'):
            while True:
                m = MATHJAX_INLINE_RE.search(line)
                if not m:
                    break
                tex = m.group(0)
                placeholder = self.md.htmlStash.store(code_escape(tex))
                line = line[:m.start()] + placeholder + line[m.end():]
            lines3.append(line)

        return lines3


def makeExtension(**kwargs):
    return MathJaxExtension(**kwargs)
