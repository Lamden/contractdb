from unittest import TestCase
from contractdb.db.chain import SQLLiteBlockStorageDriver


class TestSQLLiteBlockStorageDriver(TestCase):
    def setUp(self):
        self.chain = SQLLiteBlockStorageDriver(filename='blocks.db')

        self.chain.cursor.execute('drop table blocks')
        self.chain.cursor.execute('drop table transaction_inputs')
        self.chain.cursor.execute('drop table transaction_outputs')

        self.chain.setup()

        self.b = {
            'hash': 'hello',
            'index': 123,
            'transactions': [
                 {
                     'hash': 'xxx',
                     'index': 0,
                     'input': {
                         'sender': 'stu',
                         'signature': 'asd',
                         'payload': {
                             'contract': 'stustu',
                             'function': 'send',
                             'arguments': {
                                 'code': 123,
                                 'hello': 555
                             }
                         }
                     },
                     'output': {
                         'status': 0,
                         'updates': {
                             'stu': 'cool',
                             'monica': 'lame'
                         },
                         'result': 0,
                     }
                 },
                 {
                     'hash': 'xxy',
                     'index': 1,
                     'input': {
                         'sender': 'stu',
                         'signature': 'asd',
                         'payload': {
                             'contract': 'stustu',
                             'function': 'send',
                             'arguments': {
                                 'code': 123,
                                 'hello': 555
                             }
                         }
                     },
                     'output': {
                         'status': 0,
                         'updates': {
                             'stu': 'cool',
                             'monica': 'lame'
                         },
                         'result': 0,
                     }
                 }
             ]
        }

        self.b2 = {
            'hash': 'hello2',
            'index': 124,
            'transactions': [
                {
                    'hash': 'yyy',
                    'index': 0,
                    'input': {
                        'sender': 'afw',
                        'signature': '3y3y',
                        'payload': {
                            'contract': 'absfsd',
                            'function': 'ywwww',
                            'arguments': {
                                'code': 123,
                                'hello': 555,
                                'sdf': 'dsfg'
                            }
                        }
                    },
                    'output': {
                        'status': 0,
                        'updates': {
                            'stu': 'cool',
                            'monica': 'lame'
                        },
                        'result': 0,
                    }
                },
                {
                    'hash': 'uuu',
                    'index': 1,
                    'input': {
                        'sender': 'stu',
                        'signature': 'asd',
                        'payload': {
                            'contract': 'stustu',
                            'function': 'vvvvvvvv',
                            'arguments': {
                                'code': False,
                                'hello': True
                            }
                        }
                    },
                    'output': {
                        'status': 0,
                        'updates': {
                            'stu': 'cool',
                            'monica': 'lame'
                        },
                        'result': 0,
                    }
                }
            ]
        }

        self.chain.insert_block(self.b)
        self.chain.insert_block(self.b2)
        self.chain.conn.commit()

    def tearDown(self):
        self.chain.conn.close()

    def test_get_block_by_hash(self):
        b = self.chain.get_block_by_hash('hello')
        self.assertEqual(b, self.b)
        self.chain.conn.close()

    def test_get_block_by_index(self):
        b = self.chain.get_block_by_index(124)
        self.assertEqual(b, self.b2)
        self.chain.conn.close()

    def test_height(self):
        self.assertEqual(self.chain.height(), 124)
        self.chain.conn.close()

    def test_latest_hash(self):
        self.assertEqual(self.chain.latest_hash(), 'hello2')

    def test_get_tx_by_hash(self):
        tx = self.chain.get_transaction_by_hash('uuu')
        self.assertEqual(tx, self.b2['transactions'][1])
