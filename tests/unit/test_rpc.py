from unittest import TestCase
from contracting.server import rpc
from contracting.client import ContractingClient
from contracting.execution.executor import Executor
from contracting.utils import make_tx
import nacl.signing
import json

client = ContractingClient()


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


class TestRPC(TestCase):
    def setUp(self):
        rpc.driver.flush()

        with open('../../contracting/contracts/submission.s.py') as f:
            contract = f.read()

        rpc.driver.set_contract(name='submission',
                                code=contract,
                                author='sys')

        self.e = Executor(currency_contract='erc20_clone', metering=False)

        self.e.execute(**TEST_SUBMISSION_KWARGS,
                       kwargs=submission_kwargs_for_file('./test_sys_contracts/currency.s.py'))

    def tearDown(self):
        rpc.driver.flush()

    def test_get_contract(self):
        contract = '''
def stu():
    print('howdy partner')
'''

        name = 'stustu'
        author = 'woohoo'
        _t = 'test'

        rpc.driver.set_contract(name, contract, author=author, _type=_t)

        response = rpc.get_contract('stustu')

        self.assertEqual(response, contract)

    def test_get_contract_doesnt_exist_returns_status(self):
        response = rpc.get_contract('stustu')

        expected = {'status': 1}

        self.assertEqual(response, expected)

    def test_get_methods(self):
        contract = '''
def stu():
    print('howdy partner')
'''

        name = 'stustu'
        author = 'woohoo'
        _t = 'test'

        rpc.driver.set_contract(name, contract, author=author, _type=_t)

        response = rpc.get_methods('stustu')

        expected = [{'name': 'stu', 'arguments': []}]

        self.assertEqual(response, expected)

    def test_get_methods_doesnt_return_private_methods(self):
        response = rpc.get_methods('currency')

        expected = [{'name': 'transfer', 'arguments': ['to', 'amount']},
                    {'name': 'approve', 'arguments': ['spender', 'amount']},
                    {'name': 'transfer_from', 'arguments': ['approver', 'spender', 'amount']}]

        self.assertEqual(response, expected)

    def test_get_methods_no_contract_returns_error(self):
        response = rpc.get_methods('stustu')

        expected = {'status': 1}

        self.assertEqual(response, expected)

    def test_get_var_that_exists(self):
        response = rpc.get_var('currency', 'seed_amount')

        expected = 1000000

        self.assertEqual(response, expected)

    def test_get_var_that_doesnt_exist(self):
        response = rpc.get_var('currency', 'bleck')

        expected = {'status': 2}

        self.assertEqual(response, expected)

    def test_get_var_hash_that_exists(self):
        response = rpc.get_var('currency', 'balances', '324ee2e3544a8853a3c5a0ef0946b929aa488cbe7e7ee31a0fef9585ce398502')

        expected = 1000000

        self.assertEqual(response, expected)

    def test_get_var_hash_that_doesnt_exist(self):
        response = rpc.get_var('currency', 'balances',
                               'xxx')

        expected = {'status': 2}

        self.assertEqual(response, expected)

    def test_get_var_contract_doesnt_exist(self):
        response = rpc.get_var('xxx', 'balances',
                               'xxx')

        expected = {'status': 1}

        self.assertEqual(response, expected)

    def test_get_var_multihash_that_exists(self):
        pass

    def test_get_var_multihash_that_doesnt_exist(self):
        pass

    def test_get_vars_returns_correctly(self):
        expected = ['xrate', 'seed_amount', 'balances', 'allowed']

        response = rpc.get_vars('currency')

        self.assertEqual(response, expected)

    def test_get_vars_on_contract_doesnt_exist(self):
        response = rpc.get_vars('xxx')

        expected = {'status': 1}

        self.assertEqual(response, expected)

    def test_run_tx(self):
        rpc.driver.flush()

        with open('../../contracting/contracts/submission.s.py') as f:
            contract = f.read()

        rpc.driver.set_contract(name='submission',
                            code=contract,
                            author='sys')

        contract = '''
owner = Variable()

@construct
def seed():
    owner.set(ctx.caller)

@export
def get_owner():
    return owner.get()
        '''

        nakey = nacl.signing.SigningKey.generate()

        pk = nakey.verify_key.encode().hex()

        tx = make_tx(nakey,
                     contract='submission',
                     func='submit_contract',
                     arguments={
                        'code': contract,
                        'name': 'stu_bucks'
                    })

        result = rpc.run(tx)

        self.assertEqual(result[0], tx)

        owner = result[1]['updates'].get('stu_bucks.owner')

        self.assertEqual(owner, json.dumps(pk))

    def test_run_all_tx(self):
        rpc.driver.flush()

        with open('../../contracting/contracts/submission.s.py') as f:
            contract = f.read()

        rpc.driver.set_contract(name='submission',
                                code=contract,
                                author='sys')

        contract = '''
owner = Variable()

@construct
def seed():
    owner.set(ctx.caller)

@export
def get_owner():
    return owner.get()
                '''

        nakey = nacl.signing.SigningKey.generate()

        pk = nakey.verify_key.encode().hex()

        tx = make_tx(nakey,
                     contract='submission',
                     func='submit_contract',
                     arguments={
                         'code': contract,
                         'name': 'stu_bucks'
                     })

        tx_2 = make_tx(nakey,
                       contract='stu_bucks',
                       func='get_owner',
                       arguments={})

        result = rpc.run_all([tx, tx_2])

        self.assertEqual(result[0][0], tx)
        self.assertEqual(result[1][0], tx_2)

        owner = result[0][1]['updates'].get('stu_bucks.owner')
        accessed_owner = result[1][1]['result']

        self.assertEqual(owner, json.dumps(pk))
        self.assertEqual(accessed_owner, pk)

    def test_lint_code(self):
        code = '''
@export
def a():
    __ruh_roh__ = 'shaggy'
        '''
        err = "Line 4 : S2- Illicit use of '_' before variable : __ruh_roh__"

        res = rpc.lint(code)

        self.assertEqual(res[0], err)

    def test_compile(self):
        code = '''
@export
def public():
    private('hello')

def private(message):
    print(message)
'''

        compiled_code = '''def public():
    __private('hello')


def __private(message):
    print(message)
'''

        compiled_result = rpc.compile_code(code)

        self.assertEqual(compiled_result, compiled_code)