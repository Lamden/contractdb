from unittest import TestCase
from seneca.engine.interface import SenecaInterface
from seneca.engine.interpreter import SenecaInterpreter, ReadOnlyException, CompilationException
from os.path import join
from tests.utils import captured_output, TestInterface
import redis, unittest, seneca

test_contracts_path = seneca.__path__[0] + '/test_contracts/'

class TestSubmission(TestInterface):

    def test_publish_code_str(self):
        """
            Testing to see if the submission to Redis works.
        """
        code_str = """
@export
def ok():
    print('i am fine')
        """
        self.si.publish_code_str('crazy', 'anonymoose', code_str, keep_original=True)
        self.si.execute_code_str("""
from seneca.contracts.crazy import ok
ok()
        """)
        self.assertEqual(code_str, self.si.get_code('crazy'))

    def test_publish_bad_code(self):
        """
            Trying to import protected functions will fail
        """
        code_str = """
from test_contracts.good import one_you_cannot_export
        """
        with self.assertRaises(CompilationException) as context:
            self.si.publish_code_str('incorrect', 'anonymoose', code_str, keep_original=True)

    def test_publish_bad_code_inside_function(self):
        """
            Cannot import protected code inside a function neither.
        """
        code_str = """
def bad_code():
    from test_contracts.good import one_you_cannot_export
        """
        with self.assertRaises(ImportError) as context:
            self.si.publish_code_str('incorrect', 'anonymoose', code_str, keep_original=True)

    def test_republish_code_str_fail(self):
        """
            Republishting code to the same smart contract name will fail
        """
        self.si.publish_code_str('crazy', 'anonymoose', """
def ok():
    print('i am fine')
        """, keep_original=True)
        with self.assertRaises(Exception) as context:
            self.si.publish_code_str('crazy', 'anonymoose', """
def fail():
    print('i am not fine')
            """, keep_original=True)


if __name__ == '__main__':
    unittest.main()