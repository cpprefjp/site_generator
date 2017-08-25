# -*- coding: utf-8 -*-

import os
import re
import jsonschema


class Validator(object):
    _json_schema = {
        'type': 'object',
        'require': ['base_url', 'database_name', 'namespaces'],
        'additionalProperties': False,
        'properties': {
            'base_url': {
                'type': 'string',
                'format': 'uri-reference',
            },
            'database_name': {
                'type': 'string',
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
                                'pattern': '[^/]+',
                            },
                        },
                        'path_prefixes': {
                            'type': 'array',
                            'minItems': 1,
                            'items': {
                                'type': 'string',
                                'pattern': '[^/]+',
                            },
                        },
                        'cpp_version': {
                            'type': 'string',
                            'enum': ['98', '03', '11', '14', '17'],
                        },
                        'indexes': {
                            'type': 'array',
                            'items': {
                                'type': 'object',
                                'require': ['id'],
                                'additionalProperties': False,
                                'properties': {
                                    'id': {
                                        '$ref': '#/definitions/index_id',
                                    },
                                    'page_id': {
                                        'type': 'string',
                                        'minLength': 1,
                                    },
                                    'related_to': {
                                        'type': 'array',
                                        'items': {
                                            '$ref': '#/definitions/index_id',
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
                            'pattern': '[^"<>]+',
                        },
                    },
                    'cpp_namespace': {
                        'type': 'array',
                        'items': {
                            'type': 'string',
                            'pattern': '[^:]+',
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
                            'pattern': '[^:]+',
                        },
                    },
                    'cpp_namespace': {
                        'type': 'array',
                        'items': {
                            'type': 'string',
                            'pattern': '[^:]+',
                        },
                    },
                },
            },
        },
    }

    def validate(self, json):
        jsonschema.validate(json, self._json_schema)


class Generator(object):
    _HASH_HEADER_RE = re.compile(r'^( *?\n)*#(?P<header>.*?)#*(\n|$)(?P<remain>(.|\n)*)', re.MULTILINE)
    _SETEXT_HEADER_RE = re.compile(r'^( *?\n)*(?P<header>.*?)\n=+[ ]*(\n|$)(?P<remain>(.|\n)*)', re.MULTILINE)
    _REMOVE_ESCAPE_RE = re.compile(r'\\(.)')
    _META_RE = re.compile(r'^\s*\*\s*(?P<target>.*?)\[meta\s+(?P<name>.*?)\]\s*$')

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
        return self._REMOVE_ESCAPE_RE.sub(r'\1', m.group('header').strip()), m.group('remain')

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
        lines = md.split('\n')
        for line in lines:
            m = self._META_RE.match(line)
            if m is not None:
                target = m.group('target')
                name = m.group('name')
                if name not in result:
                    result[name] = []
                result[name].append(target)
        return result

    def make_index(self, md, names):
        title, contents = self.split_title(md)
        metas = self.get_meta(md)

        # type 判別
        # metas['id-type']: class, class template, function, function template, enum, variable, type-alias, macro, namespace
        # type: "header" / "class" / "function" / "mem_fun" / "macro" / "enum" / "variable"/ "type-alias" / "article"
        if metas['id-type'][0] == 'class' or metas['id-type'][0] == 'class template':
            type = 'class'
        elif metas['id-type'][0] == 'function' or metas['id-type'][0] == 'function template':
            if 'class' in metas:
                type = 'mem_fun'
            else:
                type = 'function'
        elif metas['id-type'][0] == 'enum':
            type = 'enum'
        elif metas['id-type'][0] == 'variable':
            type = 'variable'
        elif metas['id-type'][0] == 'type-alias':
            type = 'type-alias'

        # namespace 判別
        if 'namespace' in metas:
            cpp_namespaces = metas['namespace'][0].split('::')
        else:
            cpp_namespaces = None

        index_id = {
            'type': type,
            'key': [title],
        }

        if cpp_namespaces is not None:
            index_id['cpp_namespace'] = cpp_namespaces

        index = {
            'id': index_id,
            'page_id': names[-1][:-3], # remove .md
        }

        return index

    def generate(self, base_dir, file_paths):
        indices = []
        for file_path in file_paths:
            if not file_path.startswith(base_dir):
                raise RuntimeError(f'{file_path} not starts with {base_dir}')
            if not file_path.endswith('.md'):
                raise RuntimeError(f'{file_path} not ends with .md')

            names = list(filter(None, file_path[len(base_dir):].split('/')))
            with open(file_path) as f:
                md = f.read()
            index = self.make_index(md, names)
            indices.append((names, index))

        # names[:-1] が同じものをまとめる
        namespaces = {}
        for names, index in indices:
            xs = tuple(names[:-1])
            if xs in namespaces:
                namespaces[xs]['indexes'].append(index)
            else:
                namespace = {
                    'namespace': names[:-1],
                    'path_prefixes': names[:-1],
                    'indexes': [index],
                }
                namespaces[xs] = namespace

        namespaces = sorted(namespaces.values(), key=lambda ns: ns['namespace'])

        result = {
            'base_url': 'https://cpprefjp.github.io',
            'database_name': 'cpprefjp',
            'namespaces': namespaces,
        }
        return result


def main():
    pass

if __name__ == '__main__':
    main()
