# -*- coding: utf-8 -*-
"""
コミット構文
=========================================

コミットIDをリンクに変換する
[commit REPOSITORY_NAME, commit-id0, commit-id-2...]

    >>> text = "[commit REPOSITORY_NAME, 1234567, abcdefg]"
    >>> md = markdown.Markdown(['commit'])
    >>> print md.convert(text)
    <a href="https://github.com/REPOSITORY_NAME/commit/1234567">1234567</a> <a href="https://github.com/REPOSITORY_NAME/commit/abcdefg">abcdefg</a>
"""

import re

from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor


def replace_commit_line(line: str) -> str:
    new_line: str = line
    for m in re.finditer(r'\[commit (.*?)\]', line.strip()):
        c = m[1].split(", ")
        repo = c[0]
        links: list[str] = []
        for id in c[1:]:
            id = id.strip()
            if len(id) == 0:
                continue
            links.append("<a href=\"https://github.com/{0}/commit/{1}\">{1}</a>".format(repo, id))
        commits: str = " ".join(links)
        new_line = new_line.replace(m[0], commits)
    return new_line

class CommitExtension(Extension):

    def extendMarkdown(self, md):
        pre = CommitPreprocessor(md)

        md.registerExtension(self)
        md.preprocessors.register(pre, 'commit', 25)


class CommitPreprocessor(Preprocessor):

    def __init__(self, md):
        Preprocessor.__init__(self, md)

    def run(self, lines):
        new_lines = []

        for line in lines:
            new_line = replace_commit_line(line)
            new_lines.append(new_line)

        return new_lines


def makeExtension(**kwargs):
    return CommitExtension(**kwargs)
