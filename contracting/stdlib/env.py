from .bridge.orm import exports as orm_exports
from .bridge.hashing import exports as hash_exports
from .bridge.time import exports as time_exports
from .bridge.random import exports as random_exports
from .bridge.imports import exports as imports_exports
from .bridge.table import exports as table_exports

# TODO create a module instead and return it inside of a dictionary like:
# {
#    'stdlib': module
# }
#
# Then stdlib.datetime becomes available, etc


def gather():
    env = {}
    env.update(orm_exports)
    env.update(hash_exports)
    env.update(time_exports)
    env.update(random_exports)
    env.update(imports_exports)
    env.update(table_exports)

    return env
