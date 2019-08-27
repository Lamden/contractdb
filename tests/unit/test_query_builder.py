from unittest import TestCase
from contracting.db import query_builder
from contracting.db import filters
from contracting.db import types


class TestQueryBuilder(TestCase):
    def test_parens_single(self):
        s = query_builder.build_parenthesis({'test': 123})
        self.assertEqual(s, '(:test)')

    def test_parens_two(self):
        s = query_builder.build_parenthesis({'test': 123, 'testing': 123}, False)
        self.assertEqual(s, '(test, testing)')

    def test_parens_ten(self):
        s = query_builder.build_parenthesis({
            'a': 123, 'b': 123, 'c': 123, 'd': 123, 'e': 123, 'f': 123, 'g': 123, 'x': 123, 'y': 123, 'z': 123
        })
        self.assertEqual(s, '(:a, :b, :c, :d, :e, :f, :g, :x, :y, :z)')

    def test_build_insert_into(self):
        s = query_builder.build_insert_into(name='balances', values={
            'test':  123,
            'things': 'abd',
            'woohoo': False
        })
        self.assertEqual(s, 'INSERT INTO balances (test, things, woohoo) VALUES (:test, :things, :woohoo);')

    def test_build_table_create(self):
        s = query_builder.build_create_table_query(name='balances', values={'name': types.Int})
        self.assertEqual(s, 'CREATE TABLE IF NOT EXISTS balances (name INTEGER);')

    def test_build_table_create_multiple(self):
        s = query_builder.build_create_table_query(name='test', values={'name': types.Int,
                                                                        'another': types.Text,
                                                                        'one': types.Blob})
        self.assertEqual(s, 'CREATE TABLE IF NOT EXISTS test (name INTEGER, another TEXT, one BLOB);')

    def test_build_where(self):
        s = query_builder.build_where([filters.Eq('word', 100)])
        self.assertEqual(s, 'WHERE word = 100')

    def test_build_where_multiple(self):
        s = query_builder.build_where([filters.Eq('word', 100), filters.Gt('something', 10)])
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
        s = query_builder.build_select(columns={}, name='test', filters=[filters.Eq('test', 100)])
        self.assertEqual(s, 'SELECT * FROM test WHERE test = 100;')

    def test_build_select_with_multi_where(self):
        s = query_builder.build_select(columns={}, name='test', filters=[filters.Eq('test', 100),
                                                                         filters.Gt('hello', 1)])

        self.assertEqual(s, 'SELECT * FROM test WHERE test = 100 AND hello > 1;')

    def test_build_update(self):
        s = query_builder.build_update(name='test', sets={'test': '100', 'hello': '1'})
        self.assertEqual(s, 'UPDATE test SET test = 100 AND hello = 1;')

    def test_build_update_single(self):
        s = query_builder.build_update(name='test', sets={'test': '100'})
        self.assertEqual(s, 'UPDATE test SET test = 100;')

    def test_build_update_where(self):
        s = query_builder.build_update(name='test', sets={'test': '100'}, filters=[filters.Eq('a', 10)])
        self.assertEqual(s, 'UPDATE test SET test = 100 WHERE a = 10;')

    def test_build_update_multi_where(self):
        s = query_builder.build_update(name='test', sets={'test': '100'}, filters=[filters.Eq('a', 10),
                                                                                   filters.Gt('b', 20),
                                                                                   filters.Not('c', 3)])

        self.assertEqual(s, 'UPDATE test SET test = 100 WHERE a = 10 AND b > 20 AND c != 3;')

    def test_build_delete(self):
        s = query_builder.build_delete(name='test')
        self.assertEqual(s, 'DELETE FROM test;')

    def test_build_delete_single_filter(self):
        s = query_builder.build_delete(name='test', filters=[filters.Eq('a', 10)])
        self.assertEqual(s, 'DELETE FROM test WHERE a = 10;')

    def test_build_delete_multi_filters(self):
        s = query_builder.build_delete(name='test', filters=[filters.Eq('a', 10),
                                                             filters.Gt('b', 20),
                                                             filters.Not('c', 3)])

        self.assertEqual(s, 'DELETE FROM test WHERE a = 10 AND b > 20 AND c != 3;')