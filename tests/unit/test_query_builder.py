from unittest import TestCase
from contracting.db import query_builder


class TestQueryBuilder(TestCase):
    def test_parens_single(self):
        s = query_builder.build_parenthesis(1)
        self.assertEqual(s, '(?)')

    def test_parens_two(self):
        s = query_builder.build_parenthesis(2)
        self.assertEqual(s, '(?, ?)')

    def test_parens_ten(self):
        s = query_builder.build_parenthesis(10)
        self.assertEqual(s, '(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)')

    def test_build_insert_into(self):
        s = query_builder.build_insert_into(name='balances', values=5)
        self.assertEqual(s, 'INSERT INTO balances VALUES (?, ?, ?, ?, ?);')

    def test_build_table_create(self):
        s = query_builder.build_create_table_query(name='balances', values={'name': 'INTEGER'})
        self.assertEqual(s, 'CREATE TABLE IF NOT EXISTS balances (name INTEGER);')

    def test_build_table_create_multiple(self):
        s = query_builder.build_create_table_query(name='test', values={'name': 'INTEGER',
                                                                        'another': 'TEXT',
                                                                        'one': 'BLOB'})
        self.assertEqual(s, 'CREATE TABLE IF NOT EXISTS test (name INTEGER, another TEXT, one BLOB);')

    def test_build_where(self):
        s = query_builder.build_where(['word = 100'])
        self.assertEqual(s, 'WHERE word = 100')

    def test_build_where_multiple(self):
        s = query_builder.build_where(['word = 100', 'something > 10'])
        self.assertEqual(s, 'WHERE word = 100 AND something > 10')

    def test_build_select(self):
        s = query_builder.build_select(columns={}, name='test')
        self.assertEqual(s, 'SELECT * FROM test;')

    def test_build_select_single_column(self):
        s = query_builder.build_select(columns={'something'}, name='test')
        self.assertEqual(s, 'SELECT something FROM test;')

    def test_build_select_many_columns(self):
        s = query_builder.build_select(columns=['something', 'another', 'ones'], name='test')
        self.assertEqual(s, 'SELECT something, another, ones FROM test;')

    def test_build_select_with_single_where(self):
        s = query_builder.build_select(columns={}, name='test', filters=['test = 100'])
        self.assertEqual(s, 'SELECT * FROM test WHERE test = 100;')

    def test_build_select_with_multi_where(self):
        s = query_builder.build_select(columns={}, name='test', filters=['test = 100', 'hello > 1'])
        self.assertEqual(s, 'SELECT * FROM test WHERE test = 100 AND hello > 1;')