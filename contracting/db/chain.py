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
        self.cursor.execute('create table if not exists blocks (hash text, idx integer)')

        self.cursor.execute('create table if not exists transaction_inputs'
                            '(hash text, parent_block text, block_index integer, sender text, signature text, '
                            'contract text, function text, arguments text)')

        self.cursor.execute('create table if not exists transaction_outputs (hash text, parent_block text,'
                            'block_index integer, status integer, updates blob)')

    def get_block_by_hash(self, h: str):
        pass

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

        self.conn.commit()
