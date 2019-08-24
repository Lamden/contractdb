import sqlite3
import json

class BlockStorageDriver:
    def get_block_by_hash(self, h: str):
        raise NotImplementedError

    def get_block_by_index(self, i: int):
        raise NotImplementedError

    def get_transaction_by_hash(self, h: str):
        raise NotImplementedError

    def insert_block(self, b: dict):
        raise NotImplementedError

    @property
    def height(self):
        raise NotImplementedError

    @property
    def latest_hash(self):
        raise NotImplementedError


class SQLLiteBlockStorageDriver(BlockStorageDriver):
    def __init__(self, filename='blocks.db'):
        self.conn = sqlite3.connect(filename)
        self.cursor = self.conn.cursor()
        self.cursor.execute('create table if not exists blocks (hash text primary key, idx integer)')

        self.cursor.execute('create table if not exists transaction_inputs'
                            '(hash text primary key, parent_block text, block_index integer, sender text, '
                            'signature text, contract text, function text, arguments text)')

        self.cursor.execute('create table if not exists transaction_outputs (hash text primary key,'
                            'parent_block text, block_index integer, status integer, updates text)')

    def get_block_by_hash(self, h: str):
        self.cursor.execute('select * from blocks where hash=?', (h,))
        block = self.cursor.fetchone()

        self.cursor.execute('select * from transaction_inputs where parent_block=?', (h,))
        tx_inputs = self.cursor.fetchall()

        self.cursor.execute('select * from transaction_outputs where parent_block=?', (h,))
        tx_outputs = self.cursor.fetchall()

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
