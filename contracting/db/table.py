from collections import OrderedDict
from . import filters
from . import state

class Table:
    def __init__(self, schema: dict):
        self.schema = OrderedDict(schema)
        self.primary_key = list(self.schema.items())[0]

    # CRUD
    def insert(self, obj: dict) -> state.Result:
        raise NotImplementedError

    def select(self, keys: set, filters: filters.Filter) -> state.ReadResult:
        raise NotImplementedError

    def update(self, obj: dict, filters: filters.Filter) -> state.ReadResult:
        raise NotImplementedError

    def delete(self, obj: dict, filters: filters.Filter) -> state.Result:
        raise NotImplementedError

    # KV
    def get(self, key: str) -> dict:
        raise NotImplementedError

    def set(self, key: str, value: dict) -> bool:
        raise NotImplementedError