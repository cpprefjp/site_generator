# -*- coding: utf-8 -*-
"""
絵文字の置き換え
=========================================

絵文字を以下の方針に従って置き換える：
・表示できない環境を考慮する (アクセシビリティ)
・絵文字の意味をツールチップで表示する

    >>> text = "GCC: 12.0 [mark noimpl], 13.1 [mark impl], 14.1 [mark verified]"
    >>> md = markdown.Markdown(['mark'])
    >>> print md.convert(text)
    GCC: 12.0 <span role="img" aria-label="未実装" title="未実装">❌</span>, 13.1 <span role="img" aria-label="実装済" title="実装済">⭕</span>, 14.1 <span role="img" aria-label="検証済" title="検証済">✅</span>
"""

import re

from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor


MARK_DICT = {
    "[mark noimpl]": "<span role=\"img\" aria-label=\"未実装\" title=\"未実装\">❌</span>",
    "[mark impl]": "<span role=\"img\" aria-label=\"実装済\" title=\"実装済\">⭕</span>",
    "[mark verified]": "<span role=\"img\" aria-label=\"検証済\" title=\"検証済\">✅</span>",
}

class MarkExtension(Extension):

    def extendMarkdown(self, md):
        markpre = MarkPreprocessor(md)

        md.registerExtension(self)
        md.preprocessors.register(markpre, 'mark', 25)


class MarkPreprocessor(Preprocessor):

    def __init__(self, md):
        Preprocessor.__init__(self, md)

    def run(self, lines):
        new_lines = []
        pattern = re.compile("|".join(map(re.escape, MARK_DICT.keys())))

        for line in lines:
            new_line = pattern.sub(lambda match: MARK_DICT[match.group(0)], line)
            new_lines.append(new_line)

        return new_lines


def makeExtension(**kwargs):
    return MarkExtension(**kwargs)
