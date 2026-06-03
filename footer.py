# -*- coding: utf-8 -*-

import markdown
from markdown.util import etree


class FooterExtension(markdown.Extension):
    """Footer Extension."""
    def __init__(self, configs):
        # デフォルトの設定
        self.config = {
            'url': [None, 'URL'],
        }

        # ユーザ設定で上書き
        for key, value in configs:
            self.setConfig(key, value)

    def extendMarkdown(self, md):
        footer = FooterTreeprocessor()
        footer.config = self.getConfigs()
        md.registerExtension(self)
        #md.treeprocessors.add('footer', footer, '_begin')
        md.treeprocessors.register(footer, 'footer', 50) # top priority (begin)


class FooterTreeprocessor(markdown.treeprocessors.Treeprocessor):
    """Build and append footnote div to end of document."""
    def _make_footer(self):
        footer = etree.Element('footer')
        a = etree.SubElement(footer, 'a')
        a.set('href', self.config['url'])
        a.text = u'編集'
        return footer

    def run(self, root):
        footer = self._make_footer()
        root.append(footer)


def makeExtension(**kwargs):
    return FooterExtension(**kwargs)
