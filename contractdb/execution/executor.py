import importlib
import decimal
from contracting.execution import runtime
from contractdb.db.driver import ContractDBDriver
from contracting.execution.module import install_database_loader
from contracting import config
from contracting.db.encoder import encode

import json
import nacl.signing
import nacl.exceptions


## Create new executor that takes a transaction JSON thing and executes it. It also enforces the stamps, etc.
# if that is set in the environment variables

expected_tx_keys = {'sender', 'signature', 'payload'}
expected_tx_batch_keys = {'sender', 'signature', 'payload', 'index'}
expected_payload_keys = {'contract', 'function', 'arguments'}

MALFORMED_TX = 1
INVALID_SIG = 2
PY_EXCEPTION = 3


class Engine:
    def __init__(self, stamps_enabled=False, timestamps_enabled=False, driver=ContractDBDriver()):
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

        runtime.rt.context._base_state = {
            'signer': tx['sender'],
            'caller': tx['sender'],
            'this': tx['payload']['contract'],
            'owner': self.driver.get_owner(tx['payload']['contract'])
        }

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
