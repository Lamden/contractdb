import sys

import importlib.util
from importlib.abc import Loader, MetaPathFinder, PathEntryFinder
from importlib import invalidate_caches, __import__
from importlib.machinery import ModuleSpec
from ..db.driver import ContractDriver
from ..db.state import SQLContractStorageDriver
from ..stdlib import env
from ..execution.runtime import rt
from ..db.orm import Variable, Hash

from types import ModuleType
import marshal


# This function overrides the __import__ function, which is the builtin function that is called whenever Python runs
# an 'import' statement. If the globals dictionary contains {'__contract__': True}, then this function will make sure
# that the module being imported comes from the database and not from builtins or site packages.
#
# For all exec statements, we add the {'__contract__': True} _key to the globals to protect against unwanted imports.
#
# Note: anything installed with pip or in site-packages will also not work, so contract package names *must* be unique.
#

def restricted_import(name, globals=None, locals=None, fromlist=(), level=0):
    if globals is not None and globals.get('__contract__') is True:
        spec = importlib.util.find_spec(name)
        if not isinstance(spec.loader, DatabaseLoader):
            raise ImportError("module {} cannot be imported in a smart contract.".format(name))

    return __import__(name, globals, locals, fromlist, level)


def enable_restricted_imports():
    __builtins__['__import__'] = restricted_import


def disable_restricted_imports():
    __builtins__['__import__'] = __import__


def uninstall_builtins():
    sys.meta_path.clear()
    sys.path_hooks.clear()
    sys.path.clear()
    sys.path_importer_cache.clear()
    invalidate_caches()


def install_database_loader():
    sys.meta_path.append(DatabaseFinder)
    sys.meta_path.append(SQLDatabaseFinder)


def uninstall_database_loader():
    sys.meta_path = list(set(sys.meta_path))
    if DatabaseFinder in sys.meta_path:
        sys.meta_path.remove(DatabaseFinder)

    if SQLDatabaseFinder in sys.meta_path:
        sys.meta_path.remove(SQLDatabaseFinder)


def install_system_contracts(directory=''):
    pass


'''
    Is this where interaction with the database occurs with the interface of code strings, etc?
    IE: pushing a contract does sanity checks here?
'''


class DatabaseFinder:
    def find_spec(self, fullname, path=None, target=None):
        if MODULE_CACHE.get(self) is None:
            if ContractDriver().get_contract(self) is None:
                return None
        return ModuleSpec(self, DatabaseLoader())


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


class DatabaseLoader(Loader):
    def __init__(self):
        self.d = ContractDriver()

    def create_module(self, spec):
        return None

    def exec_module(self, module):

        # fetch the individual contract
        code = MODULE_CACHE.get(module.__name__)

        if MODULE_CACHE.get(module.__name__) is None:
            code = self.d.get_compiled(module.__name__)
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
