from unittest import TestCase
from contractdb.db.chain import SQLLiteBlockStorageDriver, \
    BlockIndexNotSequentialError, \
    BlockHashAlreadyExistsError, \
    BlockIndexAlreadyExistsError, \
    TransactionHashAlreadyExistsError
from contractdb.db.driver import ContractDBDriver

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
                            'hello': 'there',
                            'obj': [1, 2, 3]
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
                            'another': 'one',
                            'true': False
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
                            'dict': {'hi': 123},
                            'blah': 'blah'
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

    def test_storing_block_with_same_hash_fails(self):
        b = {
            'hash': 'hello',
            'index': 2,
            'transactions': []
        }

        with self.assertRaises(BlockHashAlreadyExistsError):
            self.chain.insert_block(b)

    def test_storing_block_not_sequential_fails(self):
        b = {
            'hash': 'blahblahblah',
            'index': 100,
            'transactions': []
        }

        with self.assertRaises(BlockIndexNotSequentialError):
            self.chain.insert_block(b)

    def test_storing_block_with_same_index_fails(self):
        b = {
            'hash': 'blahblahblah2',
            'index': 0,
            'transactions': []
        }

        with self.assertRaises(BlockIndexAlreadyExistsError):
            self.chain.insert_block(b)

    def test_storing_block_with_same_tx_hash_fails(self):
        b = {
            'hash': 'helloxxx',
            'index': 2,
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
                }
            ]
        }

        with self.assertRaises(TransactionHashAlreadyExistsError):
            self.chain.insert_block(b)

    def test_sync_works_as_expected(self):
        c = ContractDBDriver()

        self.chain.sync_state(c)

        self.assertEqual(c.get('stu'), 'cool')
        self.assertEqual(c.get('monica'), 'lame')
        self.assertEqual(c.get('hello'), 'there')
        self.assertEqual(c.get('obj'), [1, 2, 3])
        self.assertEqual(c.get('another'), 'one')
        self.assertEqual(c.get('true'), False)
        self.assertEqual(c.get('dict'), {'hi': 123})
        self.assertEqual(c.get('blah'), 'blah')
