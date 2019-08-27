from unittest import TestCase
from contracting.db import state
from contracting.db import types
from contracting.db import filters
import sqlite3
import os


class TestSQLConnection(TestCase):
    def setUp(self):
        self.db = sqlite3.connect('testing.db')

        self.db.execute('drop table if exists testing')
        self.db.execute('create table if not exists testing (one text, two integer)')
        self.db.commit()

    def test_connection_similar_to_regular_connection(self):
        conn = state.SQLConnection(connection=self.db)

        self.db.execute('create table if not exists testing (one text, two integer)')
        self.db.execute('insert into testing values ("hello", 123)')
        self.db.commit()

        result = conn.execute('select * from testing')

        res = result.cursor.fetchone()
        self.assertEqual(res, ('hello', 123))

    def test_results_fetchone_returns_single_record(self):
        conn = state.SQLConnection(connection=self.db)
        conn.execute('insert into testing values ("hello", 123)')
        result = conn.execute('select * from testing')

        res = result.fetchone()
        self.assertEqual(res, ('hello', 123))

    def test_results_fetchall_returns_all_records(self):
        conn = state.SQLConnection(connection=self.db)

        inserts = [('hello', 123),
                   ('there', 777),
                   ('how', 362),
                   ('are', 89372),
                   ('you', 12414)]

        for i in inserts:
            conn.execute('insert into testing values (?, ?)', i)

        result = conn.execute('select * from testing')

        res = result.fetchall()

        self.assertEqual(res, inserts)

    def test_results_for_loop_iterates_through_all(self):
        conn = state.SQLConnection(connection=self.db)

        inserts = [('hello', 123),
                   ('there', 777),
                   ('how', 362),
                   ('are', 89372),
                   ('you', 12414)]

        for i in inserts:
            conn.execute('insert into testing values (?, ?)', i)

        got = []

        result = conn.execute('select * from testing')

        for r in result:
            got.append(r)

        self.assertEqual(got, inserts)

    def test_get_item_works_in_range(self):
        conn = state.SQLConnection(connection=self.db)

        inserts = [('hello', 123),
                   ('there', 777),
                   ('how', 362),
                   ('are', 89372),
                   ('you', 12414)]

        for i in inserts:
            conn.execute('insert into testing values (?, ?)', i)

        result = conn.execute('select * from testing')

        self.assertEqual(result[0], inserts[0])
        self.assertEqual(result[1], inserts[1])
        self.assertEqual(result[2], inserts[2])
        self.assertEqual(result[3], inserts[3])
        self.assertEqual(result[4], inserts[4])

    def test_get_item_out_of_index_raises_error(self):
        conn = state.SQLConnection(connection=self.db)

        inserts = [('hello', 123),
                   ('there', 777),
                   ('how', 362),
                   ('are', 89372),
                   ('you', 12414)]

        for i in inserts:
            conn.execute('insert into testing values (?, ?)', i)

        result = conn.execute('select * from testing')

        with self.assertRaises(IndexError):
            r = result[999]
            print(r)

    def test_get_item_already_got_returns_from_retrieved_list(self):
        conn = state.SQLConnection(connection=self.db)

        inserts = [('hello', 123),
                   ('there', 777),
                   ('how', 362),
                   ('are', 89372),
                   ('you', 12414)]

        for i in inserts:
            conn.execute('insert into testing values (?, ?)', i)

        result = conn.execute('select * from testing')

        self.assertEqual(result[1], inserts[1])
        self.assertEqual(result[1], inserts[1])

    def test_double_iteration_works(self):
        conn = state.SQLConnection(connection=self.db)

        inserts = [('hello', 123),
                   ('there', 777),
                   ('how', 362),
                   ('are', 89372),
                   ('you', 12414)]

        for i in inserts:
            conn.execute('insert into testing values (?, ?)', i)

        result = conn.execute('select * from testing')

        got = []

        for r in result:
            got.append(r)

        got2 = []

        for r in result:
            got2.append(r)

        self.assertEqual(got, got2)

    def test_create_space_makes_accessible_db_with_correct_info_in_it(self):
        s = state.SQLContractStorageDriver()

        contract = 'stubucks'
        code = 'print("hello")'
        compiled = b'123'

        s.create_contract_space(contract, code, compiled)

        db = sqlite3.connect(s.get_path_for_space('stubucks'))

        c = db.execute('select * from contract')

        res = c.fetchone()

        self.assertEqual(res[0], code)
        self.assertEqual(res[1], compiled)

    def test_no_non_alpha_contracts_allowed(self):
        s = state.SQLContractStorageDriver()

        contract = 'stubucks123'
        code = 'print("hello")'
        compiled = b'123'

        self.assertFalse(s.create_contract_space(contract, code, compiled))

    def test_connect_to_space_returns_sql_connection_object(self):
        s = state.SQLContractStorageDriver()

        contract = 'stubucks'
        code = 'print("hello")'
        compiled = b'123'

        s.create_contract_space(contract, code, compiled)

        conn = s.connect_to_contract_space(contract)

        c = conn.execute('select * from contract')

        res = c.fetchone()

        self.assertEqual(res[0], code)
        self.assertEqual(res[1], compiled)

    def test_return_source_code_from_state_returns_code_str(self):
        s = state.SQLContractStorageDriver()

        contract = 'stubucks'
        code = 'print("hello")'
        compiled = b'123'

        s.create_contract_space(contract, code, compiled)

        self.assertEqual(s.source_code_for_space('stubucks'), code)

    def test_return_compiled_from_state_returns_bytecode(self):
        s = state.SQLContractStorageDriver()

        contract = 'stubucks'
        code = 'print("hello")'
        compiled = b'123'

        s.create_contract_space(contract, code, compiled)

        self.assertEqual(s.compiled_code_for_space('stubucks'), compiled)

    def test_deleting_space_removes_it_from_os(self):
        s = state.SQLContractStorageDriver()

        contract = 'stubucks'
        code = 'print("hello")'
        compiled = b'123'

        s.create_contract_space(contract, code, compiled)

        self.assertTrue(os.path.exists(s.get_path_for_space(contract)))

        s.delete_space('stubucks')

        self.assertFalse(os.path.exists(s.get_path_for_space(contract)))

    def test_insert_sqldriver_returns_result_set(self):
        s = state.SQLContractStorageDriver()

        contract = 'stubucks'
        code = 'print("hello")'
        compiled = b'123'

        s.create_contract_space(contract, code, compiled)

        d = state.SQLDriver()
        d.create_table('stubucks', 'testing', {
            'hello': types.Text,
            'there': types.Int
        })

        res = d.insert('stubucks', 'testing', {
            'hello': 'hi',
            'there': 123
        })

        self.assertTrue(isinstance(res, state.ResultSet))

        s.delete_space('stubucks')

    def test_insert_and_select_sqldriver_works(self):
        s = state.SQLContractStorageDriver()

        contract = 'stubucks'
        code = 'print("hello")'
        compiled = b'123'

        s.create_contract_space(contract, code, compiled)

        d = state.SQLDriver()
        d.create_table('stubucks', 'testing', {
            'hello': types.Text,
            'there': types.Int
        })

        obj = {
            'hello': 'hi',
            'there': 123
        }

        d.insert('stubucks', 'testing', obj)

        obj_got = d.select('stubucks', 'testing', filters=[filters.Eq('hello', 'hi')])

        res = obj_got.fetchone()

        self.assertEqual(obj, res)