from contracting.db.contract import SQLContract
from unittest import TestCase

class TestSQLContract(TestCase):
    def test_submit_works_as_expected(self):
        code = '''
@export
def return_one:
    return 1
        '''

        SQLContract.submit(name='test', code=code)