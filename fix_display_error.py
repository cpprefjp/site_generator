# -*- coding: utf-8 -*-
"""
表示崩れを事前修正
=========================================

Markdownライブラリの以下の制限を回避：

- 箇条書きの前に空行が必要な制限を回避して、自動で空行を挟む
"""

import re
import datetime

from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor

def is_item_line(line: str) -> bool:
    stripped_line = line.strip()
    m = re.match(r'^([0-9]+\.\s)', stripped_line)
    if m:
        return True

    m = re.match(r'^([*+-]\s)', stripped_line)
    if m:
        return True
    return False

def is_item_end_line(line: str) -> bool:
    if len(line) == 0:
        return True
    if re.match(r'^#+ ', line):
        return True
    return False

class FixDisplayErrorExtension(Extension):

    def extendMarkdown(self, md):
        pre = FixDisplayErrorPreprocessor(md)

        md.registerExtension(self)
        md.preprocessors.register(pre, 'fix_display_error', 28)


class FixDisplayErrorPreprocessor(Preprocessor):

    def __init__(self, md):
        Preprocessor.__init__(self, md)

    def run(self, lines):
        new_lines = []

        prev_line: str | None = None
        in_item: bool = False
        for line in lines:
            if prev_line == None:
                prev_line = line
                new_lines.append(line)
                continue

            if not is_item_line(prev_line) and not in_item and is_item_line(line):
                new_lines.append("")

            if not in_item and is_item_line(line):
                in_item = True
            if in_item and is_item_end_line(line):
                in_item = False

            prev_line = line
            new_lines.append(line)

        return new_lines


def makeExtension(**kwargs):
    return FixDisplayErrorExtension(**kwargs)
