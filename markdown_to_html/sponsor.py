# -*- coding: utf-8 -*-
"""
スポンサー表示
=========================================

スポンサーを掲載期限付きで表示する
- name : スポンサー名を指定する。ロゴ画像があればaltとして、なければ名前表示 (required)
- img : ロゴ画像へのURLを指定する (optional)
- link : リンク先URL (optional)
- size : ロゴ画像のピクセル幅サイズ (optional)
- period : スポンサーの掲載期限 (required)
- fee : 金額。生成HTMLには影響なし。スポンサーの並び替え用 (required)
- amount : 数量。月額の場合は12、1回限りは1。スポンサーの並び替え用 (optional)
- note : メモ (optional)

    >>> text = "[sponsor name:NAME, img:IMAGE_URL, link:LINK_URL, size:PIXEL_SIZE, period:YYYY/MM/DD, amount:MONEY]"
    >>> md = markdown.Markdown(['mark'])
    >>> print md.convert(text)
    <div style="text-align: center"><a href="LINK_URL"><img src="IMAGE_URL" alt="NAME" width="PIXEL_SIZE"/></a></div>

    >>> text = "[sponsor name:NAME, link:LINK_URL]"
    >>> md = markdown.Markdown(['mark'])
    >>> print md.convert(text)
    <ul><li><a href="LINK_URL">NAME</a></li></ul>
"""

import re
import datetime

from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor


def replace_sponsor_line(line: str, now: datetime.datetime) -> str:
    m = re.search(r'\[sponsor (.*?)\]', line)
    if not m:
        return line

    dict = {}
    for x in m[1].split(", "):
        y = x.split(":")
        dict[y[0]] = ":".join(y[1:])

    # check expired (one-time or canceled)
    if dict.get("period"):
        period = datetime.datetime.fromisoformat(dict["period"] + " 23:59:59.000000+09:00")
        if now > period:
            return line.replace(m[0], "")

    if dict.get("img") is None:
        new_sponsor = ""
        if dict.get("link") is None:
            new_sponsor = "<ul><li>{}</li></ul>".format(dict["name"])
        else:
            new_sponsor = "<ul><li><a href=\"{}\">{}</a></li></ul>".format(dict["link"], dict["name"])
        return line.replace(m[0], new_sponsor)

    img = ""
    center = ""
    center_close = ""
    center = "<div style=\"text-align: center\">"
    center_close = "</div>"
    img = "<img src=\"{0}\" alt=\"{1}\" title=\"{1}\"{2}/>".format(
        dict["img"],
        dict["name"],
        " width=\"{}\"".format(dict["size"]) if dict.get("size") is not None else ""
    )
    link = ""
    link_close = ""
    if dict.get("link") is not None:
        link = "<a href=\"{}\">".format(dict["link"])
        link_close = "</a>"

    new_sponsor = center + link + img + link_close + center_close
    return line.replace(m[0], new_sponsor)

class SponsorExtension(Extension):

    def extendMarkdown(self, md):
        pre = SponsorPreprocessor(md)

        md.registerExtension(self)
        md.preprocessors.register(pre, 'sponsor', 25)


class SponsorPreprocessor(Preprocessor):

    def __init__(self, md):
        Preprocessor.__init__(self, md)

    def run(self, lines):
        new_lines = []

        jst = datetime.timezone(datetime.timedelta(hours=+9), 'JST')
        now = datetime.datetime.now(jst)

        for line in lines:
            new_line = replace_sponsor_line(line, now)
            new_lines.append(new_line)

        return new_lines


def makeExtension(**kwargs):
    return SponsorExtension(**kwargs)
