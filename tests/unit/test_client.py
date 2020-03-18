from unittest import TestCase

from contractdb.client import ContractDBClient


class TestClient(TestCase):
    def setUp(self):
        self.client = ContractDBClient(socket_string='tcp://127.0.0.1:2020')

    def test_ping(self):
        d = {'result': 'ok'}
        self.assertEqual(d, self.client.ping())

    def test_get_contract(self):
        contract = '''
def stu():
    print('howdy partner')
'''