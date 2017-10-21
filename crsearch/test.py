# -*- coding: utf-8 -*-

import unittest

import run


class TestRun(unittest.TestCase):

    def test_get_meta(self):
        md = '''\
            * foo[meta text]
            * bar[meta text2]
            * piyo[meta text]
        '''
        result = run.Generator().get_meta(md)
        self.assertEqual({'text': ['foo', 'piyo'], 'text2': ['bar']}, result)

    def test_validate(self):
        value = {
            'base_url': 'https://cpprefjp.github.io',
            'database_name': 'cpprefjp',
            'ids': [{
                'type': 'header',
                'key': ['vector'],
                'cpp_namespace': ['std', 'experimental'],
            }],
            'namespaces': [
                {
                    'namespace': ['lang'],
                    'path_prefixes': ['lang', 'cpp14'],
                    'indexes': [
                        {
                            'id': 0,
                            'page_id': ['operator_at'],
                        },
                    ],
                },
            ],
        }
        run.Validator().validate(value)

    def test_generate(self):
        paths = [
            'test/reference/array.md',
            'test/reference/array/op_less.md',
            'test/reference/algorithm/all_of.md',
            'test/reference/vector.md',
            'test/reference/vector/push_back.md',
            'test/reference/vector/swap_free.md',
        ]
        value = run.Generator().generate('test', paths)
        run.Validator().validate(value)

    # def test_all(self):
    #     paths = list(run.get_files('site/article')) + list(run.get_files('site/lang')) + list(run.get_files('site/reference'))
    #     result = run.Generator().generate('site', paths)
    #     run.Validator().validate(result)


if __name__ == '__main__':
    unittest.main()
