import importlib
import decimal
from contracting.logger import get_logger
from . import runtime
from ..db.driver import ContractDriver
from ..db.state import SQLContractStorageDriver
from ..execution.module import install_database_loader, uninstall_builtins
from .. import config

from ..db.encoder import encode

import json
import nacl.signing
import nacl.exceptions

log = get_logger('Executor')

# # Support other signature schemes here
class Executor:
    def __init__(self,
                 production=False,
                 driver=ContractDriver(),
                 metering=True,
                 currency_contract='currency',
                 balances_hash='balances'):

        self.metering = metering

        self.driver = driver

        self.production = production

        self.sandbox = Sandbox()

        self.currency_contract = currency_contract
        self.balances_hash = balances_hash

        runtime.rt.env.update({'__Driver': self.driver})

    def execute(self, sender, contract_name, function_name, kwargs,
                environment={},
                driver=None,
                stamps=1000000,
                metering=None) -> tuple:

        if metering is None:
            metering = self.metering

        runtime.rt.env.update({'__Driver': self.driver})

        if driver is None:
            driver = runtime.rt.env.get('__Driver')

        status_code, result, stamps_used = self.sandbox.execute(sender, contract_name, function_name, kwargs,
                                                                environment=environment,
                                                                driver=driver,
                                                                metering=metering,
                                                                stamps=stamps,
                                                                currency_contract=self.currency_contract,
                                                                balances_hash=self.balances_hash)

        return status_code, result, stamps_used


class Sandbox(object):
    def __init__(self):
        install_database_loader()

    def wipe_modules(self):
        uninstall_builtins()
        install_database_loader()

    def execute(self, sender, contract_name, function_name, kwargs,
                environment={},
                driver=None,
                metering=None,
                stamps=1000000,
                currency_contract=None,
                balances_hash=None):

    ### Verify TX here

### EXECUTION START

        # Use _driver if one is provided, otherwise use the default _driver, ensuring to set it
        # back to default only if it was set previously to something else
        if driver:
            runtime.rt.env.update({'__Driver': driver})
        else:
            driver = runtime.rt.env.get('__Driver')

        # __main__ is replaced by the sender of the message in this case

        balances_key = None
        if metering:
            balances_key = '{}{}{}{}{}'.format(currency_contract,
                                               config.INDEX_SEPARATOR,
                                               balances_hash,
                                               config.DELIMITER,
                                               sender)

            balance = driver.get(balances_key) or 0

            assert balance * config.STAMPS_PER_TAU >= stamps, 'Sender does not have enough stamps for the transaction. \
                                                       Balance at key {} is {}'.format(balances_key, balance)

        runtime.rt.ctx.clear()
        runtime.rt.ctx.append(sender)
        runtime.rt.env.update(environment)
        runtime.rt.set_up(stmps=stamps, meter=metering)

        status_code = 0

        try:
            module = importlib.import_module(contract_name)

            func = getattr(module, function_name)

            result = func(**kwargs)

        except Exception as e:
            result = e
            status_code = 1

        runtime.rt.tracer.stop()

        # Deduct the stamps if that is enabled
        if metering:
            assert balances_key is not None, 'Balance key was not set properly. Cannot deduct stamps.'

            to_deduct = runtime.rt.tracer.get_stamp_used()
            to_deduct /= config.STAMPS_PER_TAU

            to_deduct = decimal.Decimal(to_deduct)

            balance = driver.get(balances_key) or 0
            balance -= to_deduct

            driver.set(balances_key, balance)

        stamps_used = runtime.rt.tracer.get_stamp_used()
        runtime.rt.clean_up()
        runtime.rt.env.update({'__Driver': driver})

        _driver = runtime.rt.env.get('__Driver')
        _driver.clear_sets()

        return status_code, result, stamps_used


## Create new executor that takes a transaction JSON thing and executes it. It also enforces the stamps, etc.
# if that is set in the environment variables

expected_tx_keys = {'sender', 'signature', 'payload'}
expected_tx_batch_keys = {'sender', 'signature', 'payload', 'index'}
expected_payload_keys = {'contract', 'function', 'arguments'}

MALFORMED_TX = 1
INVALID_SIG = 2
PY_EXCEPTION = 3


class Engine:
    def __init__(self, stamps_enabled=False, timestamps_enabled=False, driver=ContractDriver()):
        install_database_loader()

        self.driver = driver

        self.stamps_enabled = stamps_enabled
        self.timestamps_enabled = timestamps_enabled

    def verify_tx_structure(self, tx: dict, part_of_batch=False):
        expected_keys = expected_tx_keys if not part_of_batch else expected_tx_batch_keys
        if tx.keys() ^ expected_keys != set():
            return False

        if tx['payload'].keys() ^ expected_payload_keys != set():
            return False

        if self.stamps_enabled and not tx['payload'].get('stamps'):
            return False

        if self.timestamps_enabled and not tx['payload'].get('timestamp'):
            return False

        return True

    @staticmethod
    def verify_tx_signature(tx: dict):
        tx_payload = encode(tx['payload'])
        tx_payload_bytes = tx_payload.encode()

        signature = bytes.fromhex(tx['signature'])
        pk = bytes.fromhex(tx['sender'])

        key = nacl.signing.VerifyKey(pk)
        try:
            key.verify(tx_payload_bytes, signature)
        except nacl.exceptions.BadSignatureError:
            return False
        return True

    def run(self, tx: dict, environment={}, part_of_batch=False):
        tx_output = {
            'status': 0,
            'updates': {},
            'result': None,
        }

        # Add additional KV pair if stamps are enabled
        if self.stamps_enabled:
            tx_output['cost'] = 0

        # Verify the structure of the tx
        if not self.verify_tx_structure(tx, part_of_batch):
            tx_output['status'] = MALFORMED_TX
            return tx_output

        # Verify the signature of the tx
        if not self.verify_tx_signature(tx):
            tx_output['status'] = INVALID_SIG
            return tx_output

        # Extract the payload to pass as execution arguments
        payload = tx.get('payload')

        # Set the runtime driver (we might be able to remove this)
        runtime.rt.env.update({'__Driver': self.driver})
        runtime.rt.env.update(environment)
        runtime.rt.ctx.append(tx['sender'])

        try:
            # Access the payload values and load them from the database
            module = importlib.import_module(payload.get('contract'))
            func = getattr(module, payload.get('function'))
            tx_output['result'] = func(**payload.get('arguments'))

        except Exception as e:
            tx_output['result'] = str(e)
            tx_output['status'] = PY_EXCEPTION

        # Get the current cache of sets for the tx output

        _driver = runtime.rt.env.get('__Driver')

        tx_output['updates'] = _driver.sets

        # Clear them for the next execution
        _driver.clear_sets()

        runtime.rt.clean_up()

        return tx_output
