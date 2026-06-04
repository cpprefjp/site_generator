# -*- coding: utf-8 -*-
"""
メタデータ
=========================================

メタデータを記述できるようにする

    >>> text = '''# push_back
    ... * vector[meta header]
    ... * function[meta id-type]
    ... * std[meta namespace]
    ... * vector[meta class]
    ... * cpp11deprecated[meta cpp]
    ... * cpp14removed[meta cpp]
    ...
    ... 本文
    ... '''
    >>> md = markdown.Markdown(['meta'])
    >>> print md.convert(text)
    <h1>コードをここに書く</h1>
    <p>本文</p>
    >>> md._meta_result
    {'header': ['vector'], 'id-type': ['function'], 'namespace': ['std'], 'class': ['vector'], 'cpp': ['cpp11deprecated', 'cpp14removed']}
"""

import re

from markdown.extensions import Extension
from markdown import postprocessors
from markdown.preprocessors import Preprocessor


META_RE = re.compile(r'^\s*\*\s*(?P<target>.*?)\[meta\s+(?P<name>.*?)\]\s*$')


class MetaExtension(Extension):

    def extendMarkdown(self, md):
        metapre = MetaPreprocessor(md)
        metapost = MetaPostprocessor(md)

        md.registerExtension(self)
        md.preprocessors.register(metapre, 'meta', 25)
        md.postprocessors.register(metapost, 'meta', 0) # bottom priority (end)


class MetaPreprocessor(Preprocessor):

    def __init__(self, md):
        Preprocessor.__init__(self, md)
        self._markdown = md

    def run(self, lines):
        new_lines = []
        self._markdown._meta_result = {}
        for line in lines:
            m = META_RE.match(line)
            if m:
                target = m.group('target')
                name = m.group('name')
                if name not in self._markdown._meta_result:
                    self._markdown._meta_result[name] = []
                self._markdown._meta_result[name].append(target)
            else:
                new_lines.append(line)
        return new_lines


class MetaPostprocessor(postprocessors.Postprocessor):

    def __init__(self, md):
        postprocessors.Postprocessor.__init__(self, md)
        self._markdown = md

    CPP_DIC = {
        'future': {
            'class_name': 'future',
            'title': '将来のC++として検討中',
            'text': '(将来のC++機能)',
        },
        'archive': {
            'class_name': 'archive',
            'title': '廃案になったC++機能',
            'text': '(廃案のC++機能)',
        },
        'cpp11': {
            'class_name': 'cpp11',
            'title': 'C++11で追加',
            'text': '(C++11)',
        },
        'cpp14': {
            'class_name': 'cpp14',
            'title': 'C++14で追加',
            'text': '(C++14)',
        },
        'cpp17': {
            'class_name': 'cpp17',
            'title': 'C++17で追加',
            'text': '(C++17)',
        },
        'cpp20': {
            'class_name': 'cpp20',
            'title': 'C++20で追加',
            'text': '(C++20)',
        },
        'cpp23': {
            'class_name': 'cpp23',
            'title': 'C++23で追加',
            'text': '(C++23)',
        },
        'cpp26': {
            'class_name': 'cpp26',
            'title': 'C++26で追加',
            'text': '(C++26)',
        },
        'cpp11deprecated': {
            'class_name': 'cpp11deprecated text-warning',
            'title': 'C++11で非推奨',
            'text': '(C++11で非推奨)',
        },
        'cpp11removed': {
            'class_name': 'cpp11removed text-danger',
            'title': 'C++11で削除',
            'text': '(C++11で削除)',
        },
        'cpp14deprecated': {
            'class_name': 'cpp14deprecated text-warning',
            'title': 'C++14で非推奨',
            'text': '(C++14で非推奨)',
        },
        'cpp14removed': {
            'class_name': 'cpp14removed text-danger',
            'title': 'C++14で削除',
            'text': '(C++14で削除)',
        },
        'cpp17deprecated': {
            'class_name': 'cpp17deprecated text-warning',
            'title': 'C++17で非推奨',
            'text': '(C++17で非推奨)',
        },
        'cpp17removed': {
            'class_name': 'cpp17removed text-danger',
            'title': 'C++17で削除',
            'text': '(C++17で削除)',
        },
        'cpp20deprecated': {
            'class_name': 'cpp20deprecated text-warning',
            'title': 'C++20で非推奨',
            'text': '(C++20で非推奨)',
        },
        'cpp20removed': {
            'class_name': 'cpp20removed text-danger',
            'title': 'C++20で削除',
            'text': '(C++20で削除)',
        },
        'cpp23deprecated': {
            'class_name': 'cpp23deprecated text-warning',
            'title': 'C++23で非推奨',
            'text': '(C++23で非推奨)',
        },
        'cpp23removed': {
            'class_name': 'cpp23removed text-danger',
            'title': 'C++23で削除',
            'text': '(C++23で削除)',
        },
        'cpp26deprecated': {
            'class_name': 'cpp26deprecated text-warning',
            'title': 'C++26で非推奨',
            'text': '(C++26で非推奨)',
        },
        'cpp26removed': {
            'class_name': 'cpp26removed text-danger',
            'title': 'C++26で削除',
            'text': '(C++26で削除)',
        },
    }

    def run(self, text):
        if not hasattr(self._markdown, '_meta_result'):
            return text

        meta = self._markdown._meta_result

        text = text.replace('<h1>', '<h1><span class="token">').replace('</h1>', '</span></h1>')

        if 'cpp' in meta:
            for name in meta['cpp']:
                text = text.replace('</h1>', '<span class="cpp {class_name}" title="{title}">{text}</span></h1>'.format(**self.CPP_DIC[name]))
        if 'class' in meta:
            text = text.replace('<h1>', '<h1><span class="class" title="class {cls}">{cls}::</span>'.format(cls=meta['class'][0]))
        if 'namespace' in meta:
            text = text.replace('<h1>', '<h1><span class="namespace" title="namespace {ns}">{ns}::</span>'.format(ns=meta['namespace'][0]))
        if 'header' in meta:
            text = '<div class="header">&lt;{}&gt;</div>'.format(meta['header'][0]) + text
        if 'id-type' in meta:
            id_type = meta['id-type'][0]
            if id_type == 'cpo':
                text = '<div class="identifier-type">{}</div>'.format('customization point object') + text
            else:
                text = '<div class="identifier-type">{}</div>'.format(id_type) + text
        if 'exposition-only' in meta:
            # 見出しを斜体にするためのクラスを追加
            text = text.replace('<h1>', '<h1 class="exposition-only">')
            # 説明専用バッジを追加
            text = text.replace('</h1>', '<span class="cpp exposition-only" title="説明専用"></span></h1>')
        return text


def makeExtension(**kwargs):
    return MetaExtension(**kwargs)
