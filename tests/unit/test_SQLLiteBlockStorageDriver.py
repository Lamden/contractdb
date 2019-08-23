from unittest import TestCase
from contracting.db.chain import SQLLiteBlockStorageDriver


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

                     }
                 }
             ]}
        chain.insert_block(b)