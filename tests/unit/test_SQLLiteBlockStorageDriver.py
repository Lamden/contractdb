from unittest import TestCase
from contracting.db.chain import SQLLiteBlockStorageDriver
from pprint import pprint

class TestSQLLiteBlockStorageDriver(TestCase):
    def test_init(self):
        chain = SQLLiteBlockStorageDriver()

    def test_insert_block(self):
        chain = SQLLiteBlockStorageDriver()
        b = {'hash': 'hello',
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
                             'arguments':  {
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
                         }
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
                         }
                     }
                 }
             ]}
        chain.insert_block(b)

    def test_get_block_by_hash(self):
        chain = SQLLiteBlockStorageDriver()

        pprint(chain.get_block_by_hash('hello'))