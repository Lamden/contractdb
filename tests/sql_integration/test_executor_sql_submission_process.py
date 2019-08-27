from unittest import TestCase
from contracting.db.driver import ContractDriver
from contracting.execution.executor import Executor, Engine
from contracting.compilation.compiler import ContractingCompiler
from contracting.utils import make_tx
from contracting.db.state import SQLContractStorageDriver
import nacl.signing
import marshal

from contracting.db.state import SQLDriver

from functools import partial


def submission_kwargs_for_file(f):
    # Get the file name only by splitting off directories
    split = f.split('/')
    split = split[-1]

    # Now split off the .s
    split = split.split('.')
    contract_name = split[0]

    with open(f) as file:
        contract_code = file.read()

    return {
        'name': contract_name,
        'code': contract_code,
    }


TEST_SUBMISSION_KWARGS = {
    'sender': 'stu',
    'contract_name': 'submission',
    'function_name': 'submit_contract'
}


class TestExecutor(TestCase):
    def setUp(self):
        self.s = SQLContractStorageDriver()

        self.key = nacl.signing.SigningKey.generate()

        with open('../../contracting/contracts/submissionsql.s.py') as f:
            contract = f.read()

        self.s.create_contract_space(space='submissionsql',
                                     source_code=contract,
                                     compiled_code=marshal.dumps(contract))

        self.submit = partial(make_tx, key=self.key, contract='submissionsql', func='submit_contract')

        self.compiler = ContractingCompiler()

    def tearDown(self):
        self.s.delete_space(space='submissionsql')

    def test_submission(self):
        try:
            self.s.delete_space(space='stubucks')
        except:
            pass

        e = Engine()

        code = '''@export
def d():
    a = 1
    return 1            
'''

        kwargs = {
            'name': 'stubucks',
            'code': code
        }

        tx = self.submit(arguments=kwargs)

        out = e.run(tx)
        print(out)

        new_code = self.compiler.parse_to_code(code)

        self.assertEqual(self.s.source_code_for_space('stubucks'), new_code)
        self.s.delete_space(space='stubucks')

    def test_submission_then_function_call(self):
        try:
            self.s.delete_space(space='stubuckz')
        except:
            pass

        e = Engine()

        code = '''@export
def d():
    return 1            
'''

        kwargs = {
            'name': 'stubuckz',
            'code': code
        }

        e.run(self.submit(arguments=kwargs))
        result = e.run(make_tx(key=self.key, contract='stubuckz', func='d', arguments={}))

        self.assertEqual(result['result'], 1)
        self.assertEqual(result['status'], 0)

        self.s.delete_space(space='stubuckz')

    def test_kwarg_helper(self):
        k = submission_kwargs_for_file('./test_contracts/test_basic_table.s.py')

        code = '''t = Table({
    'hello': types.Int,
    'there': types.Text
})

@export
def insert(i, j):
    t.insert({
        'hello': i,
        'there': j
    })

@export
def select(i):
    t.select(filters=[Filters.eq('hello', i)])

    return t.fetchone()
'''

        self.assertEqual(k['name'], 'test_basic_table')
        self.assertEqual(k['code'], code)

    def test_table_insert(self):
        try:
            self.s.delete_space(space='test_basic_table')
        except:
            pass

        e = Engine(driver=SQLDriver())

        e.run(self.submit(arguments=submission_kwargs_for_file('./test_contracts/test_basic_table.s.py')))

        e.run(make_tx(self.key, 'test_basic_table', 'insert', arguments={
            'i': 1000,
            'j': 'sup'
        }))

        conn = self.s.connect_to_contract_space('test_basic_table')
        res = conn.execute('select * from t')
        r = res.fetchone()

        self.assertEqual(r, {'hello': 1000, 'there': 'sup'})

    def test_table_select(self):
        e = Engine(driver=SQLDriver())

        e.run(self.submit(arguments=submission_kwargs_for_file('./test_contracts/test_basic_table.s.py')))

        res = e.run(make_tx(self.key, 'test_basic_table', 'select', arguments={
            'i': 1000,
        }))

        self.assertEqual(res['result'], None)

    def test_table_insert_select(self):
        try:
            self.s.delete_space(space='test_basic_table')
        except:
            pass

        e = Engine(driver=SQLDriver())

        e.run(self.submit(arguments=submission_kwargs_for_file('./test_contracts/test_basic_table.s.py')))

        e.run(make_tx(self.key, 'test_basic_table', 'insert', arguments={
            'i': 1000,
            'j': 'sup'
        }))

        res = e.run(make_tx(self.key, 'test_basic_table', 'select', arguments={
            'i': 1000,
        }))

        self.assertEqual(res['result'], {'hello': 1000, 'there': 'sup'})

    def test_table_delete(self):
        try:
            self.s.delete_space(space='test_basic_table')
        except:
            pass

        e = Engine(driver=SQLDriver())

        e.run(self.submit(arguments=submission_kwargs_for_file('./test_contracts/test_basic_table.s.py')))

        e.run(make_tx(self.key, 'test_basic_table', 'insert', arguments={
            'i': 1000,
            'j': 'sup'
        }))

        e.run(make_tx(self.key, 'test_basic_table', 'delete', arguments={
            'i': 1000,
        }))

        res = e.run(make_tx(self.key, 'test_basic_table', 'select', arguments={
            'i': 1000,
        }))

        self.assertEqual(res['result'], None)

    def test_table_update(self):
        try:
            self.s.delete_space(space='test_basic_table')
        except:
            pass

        e = Engine(driver=SQLDriver())

        e.run(self.submit(arguments=submission_kwargs_for_file('./test_contracts/test_basic_table.s.py')))

        e.run(make_tx(self.key, 'test_basic_table', 'insert', arguments={
            'i': 1000,
            'j': 'sup'
        }))

        res = e.run(make_tx(self.key, 'test_basic_table', 'update', arguments={
            'i': 1000,
            'j': 'zoomzoom'
        }))

        print(res)

        res = e.run(make_tx(self.key, 'test_basic_table', 'select', arguments={
            'i': 1000,
        }))

        self.assertEqual(res['result'], {'hello': 1000, 'there': 'zoomzoom'})

    def test_orm_contract_not_accessible(self):
        e = Engine(driver=SQLDriver())

        res = e.run(make_tx(self.key, 'submissionsql', 'submit_contract',
            arguments=submission_kwargs_for_file('./test_contracts/test_orm_no_contract_access.s.py')))

        self.assertEqual(res['status'], 3)

    def test_construct_function_sets_properly(self):
        e = Engine(driver=SQLDriver())

        e.run(make_tx(self.key, 'submissionsql', 'submit_contract',
                      arguments=submission_kwargs_for_file('./test_contracts/test_construct_function_works.s.py')))

        res = e.run(make_tx(self.key, 'test_construct_function_works', 'get'))

        self.assertEqual(res['result'], {'key': 'test', 'value': '42'})

    def test_import_exported_function_works(self):
        e = Engine(driver=SQLDriver())

        e.run(make_tx(self.key, 'submissionsql', 'submit_contract',
                      arguments=submission_kwargs_for_file('./test_contracts/import_this.s.py')))

        e.run(make_tx(self.key, 'submissionsql', 'submit_contract',
                      arguments=submission_kwargs_for_file('./test_contracts/importing_that.s.py')))

        res = e.run(make_tx(self.key, 'importing_that', 'test'))

        self.assertEqual(res['result'], 12345 - 1000)

    def test_arbitrary_environment_passing_works_via_executor(self):
        e = Executor(metering=False)

        e.execute(**TEST_SUBMISSION_KWARGS,
                  kwargs=submission_kwargs_for_file('./test_contracts/i_use_env.s.py'))

        this_is_a_passed_in_variable = 555

        env = {'this_is_a_passed_in_variable': this_is_a_passed_in_variable}

        _, res, _ = e.execute('stu', 'i_use_env', 'env_var', kwargs={}, environment=env)

        self.assertEqual(res, this_is_a_passed_in_variable)

    def test_arbitrary_environment_passing_fails_if_not_passed_correctly(self):
        e = Executor(metering=False)

        e.execute(**TEST_SUBMISSION_KWARGS,
                  kwargs=submission_kwargs_for_file('./test_contracts/i_use_env.s.py'))

        this_is_a_passed_in_variable = 555

        env = {'this_is_another_passed_in_variable': this_is_a_passed_in_variable}

        status, res, _ = e.execute('stu', 'i_use_env', 'env_var', kwargs={}, environment=env)

        self.assertEqual(status, 1)
