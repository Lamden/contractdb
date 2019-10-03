import sys

from importlib.abc import Loader
from importlib.machinery import ModuleSpec
from contractdb.db.state import SQLContractStorageDriver
from contracting.stdlib import env
from contracting.execution.runtime import rt

from types import ModuleType
import marshal


def install_database_loader():
    sys.meta_path.append(SQLDatabaseFinder)


def uninstall_database_loader():
    sys.meta_path = list(set(sys.meta_path))

    if SQLDatabaseFinder in sys.meta_path:
        sys.meta_path.remove(SQLDatabaseFinder)


class SQLDatabaseFinder:
    def find_spec(self, fullname, path=None, target=None):
        if MODULE_CACHE.get(self) is None:
            try:
                if SQLContractStorageDriver().source_code_for_space(self) is None:
                    return None
            except:
                return None
            return ModuleSpec(self, SQLDatabaseLoader())


MODULE_CACHE = {}
CACHE = {}


class SQLDatabaseLoader(Loader):
    def __init__(self):
        self.s = SQLContractStorageDriver()

    def create_module(self, spec):
        return None

    def exec_module(self, module):

        # fetch the individual contract
        code = MODULE_CACHE.get(module.__name__)

        if MODULE_CACHE.get(module.__name__) is None:
            code = self.s.compiled_code_for_space(module.__name__)
            if code is None:
                raise ImportError("Module {} not found".format(module.__name__))

            if type(code) != bytes:
                code = bytes.fromhex(code)

            code = marshal.loads(code)
            MODULE_CACHE[module.__name__] = code

        if code is None:
            raise ImportError("Module {} not found".format(module.__name__))

        scope = env.gather()
        scope.update(rt.env)

        ctx = ModuleType('context')

        ctx.caller = rt.ctx[-1]
        ctx.this = module.__name__
        ctx.signer = rt.ctx[0]

        scope.update({'ctx': ctx})
        scope.update({'__contract__': True})

        rt.ctx.append(module.__name__)

        # execute the module with the std env and update the module to pass forward
        exec(code, scope)

        # Update the module's attributes with the new scope
        vars(module).update(scope)
        del vars(module)['__builtins__']

        rt.loaded_modules.append(rt.ctx.pop())

    def module_repr(self, module):
        return '<module {!r} (smart contract)>'.format(module.__name__)
