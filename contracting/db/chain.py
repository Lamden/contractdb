from contracting.db.encoder import encode
from contracting.utils import hash_bytes

import sqlite3
import json
import os


class BlockStorageDriver:
    def get_block_by_hash(self, h: str):
        raise NotImplementedError

    def get_block_by_index(self, i: int):
        raise NotImplementedError

    def get_transaction_by_hash(self, h: str):
        raise NotImplementedError

    def insert_block(self, b: dict):
        raise NotImplementedError

    def store_txs(self, txs: list):
        raise NotImplementedError

    @property
    def height(self):
        raise NotImplementedError

    @property
    def latest_hash(self):
        raise NotImplementedError


class SQLLiteBlockStorageDriver(BlockStorageDriver):
    def __init__(self, filename=os.path.expanduser('~/contracts/blocks.db')):
        self.conn = sqlite3.connect(filename)
        self.cursor = self.conn.cursor()
        self.setup()

    def setup(self):
        self.cursor.execute('create table if not exists blocks (hash text primary key, idx integer)')

        self.cursor.execute('create table if not exists transaction_inputs'
                            '(hash text primary key, parent_block text, block_index integer, sender text, '
                            'signature text, contract text, function text, arguments text)')

        self.cursor.execute('create table if not exists transaction_outputs (hash text primary key,'
                            'parent_block text, block_index integer, status integer, updates text)')

    def height(self):
        self.cursor.execute('select idx from blocks order by idx desc')
        h = self.cursor.fetchone()
        return h[0]

    def latest_hash(self):
        self.cursor.execute('select hash from blocks order by idx desc')
        h = self.cursor.fetchone()
        return h[0]

    @staticmethod
    def _build_block(block, tx_inputs, tx_outputs):
        block_dict = {
            'hash': block[0],
            'index': block[1],
            'transactions': []
        }

        # Iterate through all transactions fetched
        for i in range(len(tx_inputs)):
            # Unpack the arguments in a concise way
            tx_hash, _, idx, sender, sig, contract, func, args = tx_inputs[i]
            args_unpacked = json.loads(args)

            _, _, _, status, updates = tx_outputs[i]
            updates_unpacked = json.loads(updates)

            # Build the dict
            tx = {
                'hash': tx_hash,
                'index': idx,
                'input': {
                    'sender': sender,
                    'signature': sig,
                    'payload': {
                        'contract': contract,
                        'function': func,
                        'arguments': args_unpacked
                    }
                },
                'output': {
                    'status': status,
                    'updates': updates_unpacked
                }
            }

            # Add the dict to the transactions list
            block_dict['transactions'].append(tx)

        # Sort transactions by index
        sorted(block_dict['transactions'], key=lambda t: t['index'])

        return block_dict

    def get_block_by_hash(self, h: str):
        self.cursor.execute('select * from blocks where hash=?', (h,))
        block = self.cursor.fetchone()

        self.cursor.execute('select * from transaction_inputs where parent_block=?', (h,))
        tx_inputs = self.cursor.fetchall()

        self.cursor.execute('select * from transaction_outputs where parent_block=?', (h,))
        tx_outputs = self.cursor.fetchall()

        return self._build_block(block, tx_inputs, tx_outputs)

    def get_block_by_index(self, i: int):
        self.cursor.execute('select * from blocks where idx=?', (i,))
        block = self.cursor.fetchone()

        h = block[0]
        self.cursor.execute('select * from transaction_inputs where parent_block=?', (h,))
        tx_inputs = self.cursor.fetchall()

        self.cursor.execute('select * from transaction_outputs where parent_block=?', (h,))
        tx_outputs = self.cursor.fetchall()

        return self._build_block(block, tx_inputs, tx_outputs)

    def get_transaction_by_hash(self, h: str):
        self.cursor.execute('select * from transaction_inputs where hash=?', (h,))
        tx_input = self.cursor.fetchone()

        self.cursor.execute('select * from transaction_outputs where hash=?', (h,))
        tx_output = self.cursor.fetchone()

        tx_hash, _, idx, sender, sig, contract, func, args = tx_input
        args_unpacked = json.loads(args)

        _, _, _, status, updates = tx_output
        updates_unpacked = json.loads(updates)

        # Build the dict
        tx = {
            'hash': tx_hash,
            'index': idx,
            'input': {
                'sender': sender,
                'signature': sig,
                'payload': {
                    'contract': contract,
                    'function': func,
                    'arguments': args_unpacked
                }
            },
            'output': {
                'status': status,
                'updates': updates_unpacked
            }
        }

        return tx

    def insert_block(self, b: dict):
        self.cursor.execute('insert into blocks values (?, ?)', (b['hash'], b['index']))

        for transaction in b['transactions']:

            args = json.dumps(transaction['input']['payload']['arguments'])
            self.cursor.execute('insert into transaction_inputs values (?, ?, ?, ?, ?, ?, ?, ?)',
                                (transaction['hash'],
                                 b['hash'],
                                 transaction['index'],
                                 transaction['input']['sender'],
                                 transaction['input']['signature'],
                                 transaction['input']['payload']['contract'],
                                 transaction['input']['payload']['function'],
                                 args))

            updates = json.dumps(transaction['output']['updates'])
            self.cursor.execute('insert into transaction_outputs values (?, ?, ?, ?, ?)',
                                (transaction['hash'],
                                 b['hash'],
                                 transaction['index'],
                                 transaction['output']['status'],
                                 updates))

        self.conn.commit()

    def store_txs(self, txs: list):
        # Calculate the new hash, index, and return the results after storing
        block_hash = hash_bytes(encode(txs).encode())
        index = self.height() + 1

        block_dict = {
            'hash': block_hash,
            'index': index,
            'transactions': txs
        }

        self.insert_block(block_dict)

        return block_dict
