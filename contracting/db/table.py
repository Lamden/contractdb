from collections import OrderedDict
from . import filters
from . import state
from . import query_builder


class Table:
    def __init__(self, name: str, schema: dict, connection: state.Connection):
        self.name = name
        self.schema = OrderedDict(schema)
        self.primary_key = list(self.schema.items())[0]
        self.connection = connection

    # CRUD
    def insert(self, obj: dict) -> state.ResultSet:
        raise NotImplementedError

    def select(self, columns: set, filters: filters.Filter) -> state.ResultSet:
        raise NotImplementedError

    def update(self, obj: dict, filters: filters.Filter) -> state.ResultSet:
        raise NotImplementedError

    def delete(self, obj: dict, filters: filters.Filter) -> state.ResultSet:
        raise NotImplementedError

    # KV
    def get(self, key: str) -> dict:
        raise NotImplementedError

    def set(self, key: str, value: dict) -> bool:
        raise NotImplementedError


class SQLTable(Table):
    def __init__(self, name: str, schema: dict, connection: state.Connection):
        super().__init__(name, schema, connection)

        self.connection.execute(
            query_builder.build_create_table_query(name=self.name, values=self.schema)
        )

    def insert(self, obj: dict):
        q = query_builder.build_insert_into(self.name, obj)
        return self.connection.execute(q)

    def select(self, columns: set, filters: filters.Filter):
        q = query_builder.build_select(name=self.name, columns=columns, filters=filters)
        return self.connection.execute(q)

    def update(self, sets={}, filters=[]):
        q = query_builder.build_update(name=self.name, sets=sets, filters=filters)
        return self.connection.execute(q)

    def delete(self):
        pass