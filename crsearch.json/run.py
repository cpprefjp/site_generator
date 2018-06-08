# -*- coding: utf-8 -*-

import json
import os
import re
from itertools import chain

import jsonschema


class Validator(object):
    _json_schema = {
        'type': 'object',
        'require': ['base_url', 'database_name', 'namespaces', 'ids'],
        'additionalProperties': False,
        'properties': {
            'base_url': {
                'type': 'string',
                'format': 'uri-reference',
            },
            'database_name': {
                'type': 'string',
            },
            'ids': {
                'type': 'array',
                'items': {
                    '$ref': '#/definitions/index_id',
                },
            },
            'namespaces': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'require': ['namespace', 'path_prefixes', 'indexes'],
                    'additionalProperties': False,
                    'properties': {
                        'namespace': {
                            'type': 'array',
                            'minItems': 1,
                            'items': {
                                'type': 'string',
                                'pattern': '^[^/]+$',
                            },
                        },
                        'path_prefixes': {
                            'type': 'array',
                            'minItems': 1,
                            'items': {
                                'type': 'string',
                                'pattern': '^[^/]+$',
                            },
                        },
                        'cpp_version': {
                            'type': 'string',
                            'enum': ['98', '03', '11', '14', '17', '20'],
                        },
                        'indexes': {
                            'type': 'array',
                            'items': {
                                'type': 'object',
                                'require': ['id'],
                                'additionalProperties': False,
                                'properties': {
                                    'id': {
                                        'type': 'integer',
                                    },
                                    'page_id': {
                                        'type': 'array',
                                        'minItems': 1,
                                        'items': {
                                            'type': 'string',
                                            'pattern': '^[^/]+$',
                                        },
                                    },
                                    'related_to': {
                                        'type': 'array',
                                        'items': {
                                            'type': 'integer',
                                        },
                                    },
                                    'nojump': {
                                        'type': 'boolean',
                                    },
                                    'attributes': {
                                        'type': 'array',
                                        'items': {
                                            'type': 'string',
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
        },
        'definitions': {
            'index_id': {
                'type': 'object',
                'oneOf': [
                    {'$ref': '#/definitions/header'},
                    {'$ref': '#/definitions/common'},
                ],
            },
            'header': {
                'require': ['type', 'key'],
                'additionalProperties': False,
                'properties': {
                    'type': {
                        'type': 'string',
                        'enum': ['header'],
                    },
                    'key': {
                        'type': 'array',
                        'items': {
                            'type': 'string',
                            'pattern': '^[^"<>]+$',
                        },
                    },
                    'cpp_namespace': {
                        'type': 'array',
                        'items': {
                            'type': 'string',
                            'pattern': '^[^:]+$',
                        },
                    },
                },
            },
            'common': {
                'require': ['type', 'key'],
                'additionalProperties': False,
                'properties': {
                    'type': {
                        'type': 'string',
                        'enum': ['class', 'function', 'mem_fun', 'macro', 'enum', 'variable', 'type-alias', 'article'],
                    },
                    'key': {
                        'type': 'array',
                        'items': {
                            'type': 'string',
                            'pattern': '^[^:]+$',
                        },
                    },
                    'cpp_namespace': {
                        'type': 'array',
                        'items': {
                            'type': 'string',
                            'pattern': '^[^:]+$',
                        },
                    },
                },
            },
        },
    }

    def validate(self, json):
        jsonschema.validate(json, self._json_schema)


class Generator(object):
    class IndexIDGenerator(object):
        def __init__(self):
            self._ids = []

        def get_indexid(self, indexid):
            for n, id in enumerate(self._ids):
                if indexid == id:
                    return n
            n = len(self._ids)
            self._ids.append(indexid)
            return n

        def get_all(self):
            return self._ids

    _CPP_LATEST_VERSION = '20'
    _CPP_LATEST = 'cpp' + _CPP_LATEST_VERSION
    _CPP_RE_RAW = r'cpp\d+[a-zA-Z]?'

    _NOT_ATTRIBUTE_RE = re.compile(_CPP_RE_RAW)
    _DEPRECATED_IN_CPP_RE = re.compile(_CPP_RE_RAW + r'deprecated')
    _REMOVED_IN_CPP_RE = re.compile(_CPP_RE_RAW + r'removed')

    _HASH_HEADER_RE   = re.compile(r'(?:[ \t]*\n)*#(.*)#*(?:\n|\Z)')
    _SETEXT_HEADER_RE = re.compile(r'(?:[ \t]*\n)*(.*)\n=+ *(?:\n|\Z)')
    _REMOVE_ESCAPE_RE = re.compile(r'\\(.)')
    _META_RE = re.compile(r'^\s*\*\s*(?P<target>.*?)\[meta\s+(?P<name>.*?)\]\s*$', re.MULTILINE)

    def split_title(self, md):
        r"""先頭の見出し部分を（あるなら）取り出す

        >>> md = '''
        ... # header
        ...
        ... contents
        ... '''
        >>> Generator().split_title(md)
        ('header', '\ncontents\n')
        >>> md = '''
        ... header
        ... ======
        ...
        ... contents
        ... '''
        >>> Generator().split_title(md)
        ('header', '\ncontents\n')
        >>> md = '''
        ... contents
        ... '''
        >>> Generator().split_title(md)
        (None, '\ncontents\n')
        """
        m = self._HASH_HEADER_RE.match(md)
        if m is None:
            m = self._SETEXT_HEADER_RE.match(md)
        if m is None:
            return None, md
        return self._REMOVE_ESCAPE_RE.sub(r'\1', m.group(1).strip()), md[m.end():]

    def get_meta(self, md):
        """メタ情報を取り出す

        >>> md = '''
        ... # foo
        ...
        ... content
        ...
        ... * foo[meta text]
        ... * bar[meta text2]
        ... * piyo[meta text]
        ... '''
        {'text': ['foo', 'piyo'], 'text2': ['bar']}
        """
        result = {}
        for m in self._META_RE.finditer(md):
            name = m.group('name')
            if name not in result:
                result[name] = []
            if name == 'class':
                result[name] += m.group('target').split('::')
            else:
                result[name].append(m.group('target'))

        return result

    def make_index(self, md, names, idgen, nojump):
        title, contents = self.split_title(md)
        metas = self.get_meta(contents)

        # type 判別
        # metas['id-type']: class, class template, function, function template, enum, variable, type-alias, macro, namespace
        # type: "header" / "class" / "function" / "mem_fun" / "macro" / "enum" / "variable"/ "type-alias" / "article"
        if nojump:
            type = 'meta'
        elif 'id-type' not in metas:
            if 'header' in metas:
                type = 'header'
            elif names[0] == 'article':
                # それ以外の article/ の下は article 扱いにする
                type = 'article'
            elif names[0] == 'lang':
                # lang/ 直下は meta 扱いにする
                if len(names) == 2:
                    type = 'meta'
                else:
                    # それ以外の lang/ の下は article 扱いにする
                    type = 'article'
            elif names[0] == 'reference' and len(names) >= 2 and names[1] in {'concepts', 'container_concepts'}:
                # 特殊扱い
                type = 'article'
            else:
                raise RuntimeError(f'unexpected meta: {metas}')
        else:
            id_type = metas['id-type'][0]
            if id_type in {'class', 'class template'}:
                type = 'class'
            elif id_type in {'function', 'function template'}:
                if 'class' in metas or 'class template' in metas:
                    type = 'mem_fun'
                else:
                    type = 'function'
            elif id_type in {'enum', 'variable', 'type-alias', 'macro', 'namespace'}:
                type = id_type
            else:
                raise RuntimeError(f'unexpected meta: {metas}')

        if 'class' in metas:
            keys = metas['class']
        elif 'class template' in metas:
            keys = metas['class template']
        else:
            keys = []

        index_id = {
            'type': type,
            'key': keys + [title],
        }

        # namespace 判別
        if 'namespace' in metas and not nojump:
            index_id['cpp_namespace'] = metas['namespace'][0].split('::')

        index = {
            'id': idgen.get_indexid(index_id),
            # トップレベルの要素は page_id を空にする
            'page_id': [''] if len(names) == 1 else names[1:],
        }

        if nojump:
            index['nojump'] = True

        related_to = []
        if 'class' in metas:
            related_to.append(idgen.get_indexid({
                'type': 'class',
                'key': metas['class'][0].split('::'),
            }))
        if 'header' in metas:
            related_to.append(idgen.get_indexid({
                'type': 'header',
                'key': metas['header'][0].split('/'),
            }))

        if len(related_to) != 0:
            index['related_to'] = related_to

        if 'cpp' in metas:
            attributes = [cpp for cpp in metas['cpp'] if not self._NOT_ATTRIBUTE_RE.fullmatch(cpp)]
            if attributes:
                if any([attr for attr in attributes if self._REMOVED_IN_CPP_RE.fullmatch(attr)]):
                    attributes.append('removed_in_latest')

                elif any([attr for attr in attributes if self._DEPRECATED_IN_CPP_RE.fullmatch(attr)]):
                    attributes.append('deprecated_in_latest')

                index['attributes'] = attributes

        return index, metas

    def generate(self, base_dir, file_paths, all_file_paths):
        idgen = Generator.IndexIDGenerator()

        file_path_set = set(file_paths)

        namespaces = {}
        for file_path in all_file_paths:
            print(f'processing {file_path}...')
            names = list(file_path[len(base_dir) + 1:-3].split('/'))
            with open(file_path) as f:
                md = f.read()
            nojump = file_path not in file_path_set
            index, metas = self.make_index(md, names, idgen, nojump)
            # C++ のバージョン情報を入れる
            cpp_version = None
            if 'cpp' in metas:
                if any(map(lambda cpp: cpp == 'cpp11', metas['cpp'])):
                    cpp_version = '11'
                elif any(map(lambda cpp: cpp == 'cpp14', metas['cpp'])):
                    cpp_version = '14'
                elif any(map(lambda cpp: cpp == 'cpp17', metas['cpp'])):
                    cpp_version = '17'
                elif any(map(lambda cpp: cpp == 'cpp20', metas['cpp'])):
                    cpp_version = '20'

            # (names[0], cpp_version) が同じものをまとめる
            name = names[0]
            key = (name, cpp_version)
            if key in namespaces:
                namespaces[key]['indexes'].append(index)
            else:
                namespace = {
                    'namespace': [name],
                    'path_prefixes': [name],
                    'indexes': [index],
                }
                if cpp_version is not None:
                    namespace['cpp_version'] = cpp_version
                if len(names) == 1:
                    # トップレベルの場合は name を追加
                    namespace['name'] = idgen.get_all()[index['id']]['key'][0]

                namespaces[key] = namespace

        namespaces = sorted(namespaces.values(), key=lambda ns: ns['namespace'])

        result = {
            'base_url': '/',
            'database_name': 'cpprefjp',
            'namespaces': namespaces,
            'ids': idgen.get_all(),
        }
        return result


def get_files(base_dir):
    for dirpath, dirnames, filenames in os.walk(base_dir):
        for filename in filenames:
            if filename[-3:] == ".md" and not filename[:-3].isupper():
                yield os.path.join(dirpath, filename)


def main():
    _KNOWN_DIRS = [
        'site/article', 'site/lang', 'site/reference',
    ]

    paths = chain.from_iterable([get_files(d) for d in _KNOWN_DIRS])
    all_paths = list(get_files('site'))
    result = Generator().generate('site', paths, all_paths)
    with open('crsearch.json', 'wb') as f:
        f.write(json.dumps(result, separators=(',', ':'), ensure_ascii=False, sort_keys=True).encode('utf-8'))


if __name__ == '__main__':
    main()
