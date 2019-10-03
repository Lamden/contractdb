from contracting.compilation.compiler import ContractingCompiler
from contractdb.db.driver import ContractDBDriver
from contracting.execution.runtime import rt
from types import ModuleType
from contracting.stdlib import env
from contracting import config
import marshal
from .state import SQLContractStorageDriver

driver = rt.env.get('__Driver') or ContractDBDriver()
spaces = rt.env.get('__Spaces') or SQLContractStorageDriver()


class SQLContract:
    def __init__(self, spaces: SQLContractStorageDriver=spaces):
        self._spaces = spaces

    def submit(self, name, code, constructor_args={}):
        c = ContractingCompiler(module_name=name)
        code_str = c.parse_to_code(code, lint=True)

        ctx = ModuleType('context')

        ctx.caller = rt.ctx[-1]
        ctx.this = name
        ctx.signer = rt.ctx[0]

        scope = env.gather()
        scope.update({'ctx': ctx})
        scope.update({'__contract__': True})
        scope.update(rt.env)

        exec(code_str, scope)

        if scope.get(config.INIT_FUNC_NAME) is not None:
            scope[config.INIT_FUNC_NAME](**constructor_args)

        code_obj = compile(code_str, '', 'exec')
        code_blob = marshal.dumps(code_obj)

        self._spaces.create_contract_space(space=name, source_code=code_str, compiled_code=code_blob)
