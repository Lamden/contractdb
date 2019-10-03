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
            'index': 0,
            'transactions': [
                 {
                     'hash': 'xxx',
                     'input': {
                         'index': 0,
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
                         'result': {}
                     }
                 },
                 {
                     'hash': 'xxy',
                     'input': {
                         'index': 1,
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
                         'result': {}
                     }
                 }
             ]
        }

        self.b2 = {
            'hash': 'hello2',
            'index': 1,
            'transactions': [
                {
                    'hash': 'yyy',
                    'input': {
                        'index': 0,
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
                        'result': {}
                    }
                },
                {
                    'hash': 'uuu',
                    'input': {
                        'index': 1,
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
                        'result': {}
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

    def test_get_block_by_index(self):
        b = self.chain.get_block_by_index(1)
        self.assertEqual(b, self.b2)

    def test_height(self):
        self.assertEqual(self.chain.height(), 1)

    def test_latest_hash(self):
        self.assertEqual(self.chain.latest_hash(), 'hello2')

    def test_get_tx_by_hash(self):
        tx = self.chain.get_transaction_by_hash('uuu')
        self.assertEqual(tx, self.b2['transactions'][1])
