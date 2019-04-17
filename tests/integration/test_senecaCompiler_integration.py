from unittest import TestCase
from seneca.execution.compiler import SenecaCompiler
from seneca.db.orm import Variable, ForeignVariable

import astor
from types import ModuleType


class TestSenecaCompiler(TestCase):
    def test_visit_assign_variable(self):
        code = '''
v = Variable()
'''
        c = SenecaCompiler()
        comp = c.parse(code, lint=False)
        code_str = astor.to_source(comp)

        env = {'Variable': Variable}

        exec(code_str, env)

        v = env['v']

        self.assertEqual(v.key, '__main__.v')

    def test_visit_assign_foreign_variable(self):
        code = '''
fv = ForeignVariable(foreign_contract='scoob', foreign_name='kumbucha')
        '''
        c = SenecaCompiler()
        comp = c.parse(code, lint=False)
        code_str = astor.to_source(comp)

        env = {'ForeignVariable': ForeignVariable}

        exec(code_str, env)

        fv = env['fv']

        self.assertEqual(fv.key, '__main__.fv')
        self.assertEqual(fv.foreign_key, 'scoob.kumbucha')