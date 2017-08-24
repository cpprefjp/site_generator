# -*- coding: utf-8 -*-

import json
import textwrap
import unittest

import run


class TestRun(unittest.TestCase):

    def test_get_meta(self):
        md = '''\
            * foo[meta text]
            * bar[meta text2]
            * piyo[meta text]
        '''
        result = run.get_meta(md)
        self.assertEqual({'text': ['foo', 'piyo'], 'text2': ['bar']}, result)

    def test_validate(self):
        value = {
            'base_url': 'https://cpprefjp.github.io',
            'database_name': 'cpprefjp',
            'namespaces': [
                {
                    'namespace': ['lang'],
                    'path_prefixes': ['lang', 'cpp14'],
                    'indexes': [
                        {
                            'id': {
                                'type': 'header',
                                'key': ['vector'],
                            },
                            'cpp_namespace': ['std', 'experimental'],
                            'page_id': 'operator_at',
                        },
                    ],
                },
            ],
        }
        run.Validator().validate(value)

    def test_convert(self):
        pass

if __name__ == '__main__':
    unittest.main()
