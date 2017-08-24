# -*- coding: utf-8 -*-

import re
import jsonschema


META_RE = re.compile(r'^\s*\*\s*(?P<target>.*?)\[meta\s+(?P<name>.*?)\]\s*$')


def get_meta(md):
    """メタ情報を取り出す"""
    result = {}
    lines = md.split('\n')
    for line in lines:
        m = META_RE.match(line)
        if m is not None:
            target = m.group('target')
            name = m.group('name')
            if name not in result:
                result[name] = []
            result[name].append(target)
    return result


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
                                'require': ['id', 'page_id'],
                                'additionalProperties': False,
                                'properties': {
                                    'id': {
                                        '$ref': '#/definitions/index_id',
                                    },
                                    'cpp_namespace': {
                                        'type': 'array',
                                        'items': {
                                            'type': 'string',
                                            'pattern': '[^:]+',
                                        },
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
                },
            },
        },
    }

    def validate(self, json):
        jsonschema.validate(json, self._json_schema)


# class Generator(object):
#     def make_namespace(md):
#         'namespace'
#     def generate(file_paths):
#         namespaces = []
#         for file_path in file_paths:
#             with open(file_path) as f:
#                 md = f.read()
#             
#             ns = make_namespace(md)
#             namespaces.append(ns)
#         result = {
#             'base_url': 'https://cpprefjp.github.io',
#             'database_name': 'cpprefjp',
#             'namespaces': namespaces,
#         }
#         return result


def main():
    pass

if __name__ == '__main__':
    main()
