from unittest import TestCase
import nacl.signing
import json
from contractdb.engine import Engine
from contractdb.driver import ContractDBDriver
from contractdb.utils import make_tx
from contracting.db.encoder import encode

driver = ContractDBDriver()


class TestEngine(TestCase):
    def tearDown(self):
        driver.flush()

    def test_verify_good_tx_structure(self):
        tx = {
            'sender': 'public key in hex',
            'signature': 'hex of payload which is alphabetized json for now...',
            'payload': {
                'contract': 'string',
                'function': 'string',
                'arguments': {
                    'string': 123,
                }
            }
        }

        e = Engine()
        self.assertTrue(e.verify_tx_structure(tx))

    def test_verify_bad_tx_missing_key(self):
        tx = {
            'signature': 'hex of payload which is alphabetized json for now...',
            'payload': {
                'contract': 'string',
                'function': 'string',
                'arguments': {
                    'string': 123,
                }
            }
        }

        e = Engine()
        self.assertFalse(e.verify_tx_structure(tx))

    def test_verify_bad_tx_payload_key(self):
        tx = {
            'sender': 'public key in hex',
            'signature': 'hex of payload which is alphabetized json for now...',
            'payload': {
                'function': 'string',
                'arguments': {
                    'string': 123,
                }
            }
        }

        e = Engine()
        self.assertFalse(e.verify_tx_structure(tx))

    def test_verify_tx_fails_if_expecting_stamps(self):
        tx = {
            'sender': 'public key in hex',
            'signature': 'hex of payload which is alphabetized json for now...',
            'payload': {
                'contract': 'string',
                'function': 'string',
                'arguments': {
                    'string': 123,
                }
            }
        }

        e = Engine(stamps_enabled=True)
        self.assertFalse(e.verify_tx_structure(tx))

    def test_verify_tx_fails_if_expecting_timestamp(self):
        tx = {
            'sender': 'public key in hex',
            'signature': 'hex of payload which is alphabetized json for now...',
            'payload': {
                'contract': 'string',
                'function': 'string',
                'arguments': {
                    'string': 123,
                }
            }
        }

        e = Engine(timestamps_enabled=True)
        self.assertFalse(e.verify_tx_structure(tx))

    def test_verify_tx_signature_succeeds(self):
        nakey = nacl.signing.SigningKey.generate()

        pk = nakey.verify_key.encode().hex()

        tx = {
            'sender': pk,
            'signature': None,
            'payload': {
                'contract': 'string',
                'function': 'string',
                'arguments': {
                    'string': 123,
                }
            }
        }

        message = json.dumps(tx['payload']).encode()

        sig = nakey.sign(message)[:64].hex()

        tx['signature'] = sig

        e = Engine()

        self.assertTrue(e.verify_tx_signature(tx))

    def test_verify_tx_signature_fails(self):
        nakey = nacl.signing.SigningKey.generate()

        pk = nakey.verify_key.encode().hex()

        tx = {
            'sender': pk,
            'signature': None,
            'payload': {
                'contract': 'string',
                'function': 'string',
                'arguments': {
                    'string': 123,
                }
            }
        }

        message = json.dumps(tx['payload']).encode()

        sig = nakey.sign(message)[:64].hex()

        tx['signature'] = sig[:2]

        e = Engine()

        self.assertFalse(e.verify_tx_signature(tx))

    def test_submission_contract_works_on_engine(self):
        driver.flush()

        with open('../../contractdb/contracts/submission.s.py') as f:
            contract = f.read()

        print(contract)

        driver.set_contract(name='submission',
                            code=contract)

        driver.commit()

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

        tx = {
            'sender': pk,
            'signature': None,
            'payload': {
                'contract': 'submission',
                'function': 'submit_contract',
                'arguments': {
                    'code': contract,
                    'name': 'stu_bucks'
                }
            }
        }

        message = json.dumps(tx['payload']).encode()

        sig = nakey.sign(message)[:64].hex()

        tx['signature'] = sig

        e = Engine()

        output = e.run(tx)

        print(output)

        owner = output['updates'].get('stu_bucks.owner')

        self.assertEqual(owner, json.dumps(pk))

    def test_make_tx(self):
        nakey = nacl.signing.SigningKey.generate()

        pk = nakey.verify_key.encode().hex()

        tx = {
            'sender': pk,
            'signature': None,
            'payload': {
                'contract': 'submission',
                'function': 'submit_contract',
                'arguments': {
                    'code': 'test',
                    'name': 'stu_bucks'
                }
            }
        }

        message = encode(tx['payload']).encode()

        sig = nakey.sign(message)[:64].hex()

        tx['signature'] = sig

        made_tx = make_tx(nakey, contract='submission', func='submit_contract', arguments={
                    'code': 'test',
                    'name': 'stu_bucks'
                })

        self.assertEqual(made_tx, tx)

    def test_engine_returns_malformed_tx_when_run(self):
        tx = {
            'signature': 'hex of payload which is alphabetized json for now...',
            'payload': {
                'contract': 'string',
                'function': 'string',
                'arguments': {
                    'string': 123,
                }
            }
        }

        e = Engine()

        output = e.run(tx)
        self.assertEqual(output['status'], 1)

    def test_engine_returns_bad_sig_when_run(self):
        nakey = nacl.signing.SigningKey.generate()

        pk = nakey.verify_key.encode().hex()

        tx = {
            'sender': pk,
            'signature': None,
            'payload': {
                'contract': 'string',
                'function': 'string',
                'arguments': {
                    'string': 123,
                }
            }
        }

        message = json.dumps(tx['payload']).encode()

        sig = nakey.sign(message)[:64].hex()

        tx['signature'] = sig[:2]

        e = Engine()

        output = e.run(tx)

        self.assertEqual(output['status'], 2)

    def test_engine_raises_py_exception_if_assert_fails(self):
        driver.flush()

        with open('../../contractdb/contracts/submission.s.py') as f:
            contract = f.read()

        driver.set_contract(name='submission',
                            code=contract)

        contract = '''
        owner = Variable()

        @construct
        def seed():
            owner.set(ctx.caller)
                '''

        nakey = nacl.signing.SigningKey.generate()

        pk = nakey.verify_key.encode().hex()

        tx = {
            'sender': pk,
            'signature': None,
            'payload': {
                'contract': 'submission',
                'function': 'submit_contract',
                'arguments': {
                    'code': contract,
                    'name': 'stu_bucks'
                }
            }
        }

        message = json.dumps(tx['payload']).encode()

        sig = nakey.sign(message)[:64].hex()

        tx['signature'] = sig

        e = Engine()

        output = e.run(tx)

        self.assertEqual(output['status'], 3)