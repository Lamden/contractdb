from collections import OrderedDict
from . import filters
from . import state
from . import query_builder


class Table:
    def __init__(self, contract, name, driver, schema):
        self.contract = contract
        self.name = name
        self.schema = OrderedDict(schema)
        self.primary_key = list(self.schema.items())[0]
        self.connection = driver

    # CRUD
    def insert(self, obj: dict) -> state.ResultSet:
        raise NotImplementedError

    def select(self, columns: set, filters: filters.Filter) -> state.ResultSet:
        raise NotImplementedError

    def update(self, obj: dict, filters: filters.Filter) -> state.ResultSet:
        raise NotImplementedError

    def delete(self, filters: filters.Filter) -> state.ResultSet:
        raise NotImplementedError


class SQLTable(Table):
    def __init__(self, contract, name, driver: state.SQLDriver, schema):
        super().__init__(contract, name, driver, schema)

        self.connection.create_table(
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

    def delete(self, filters=[]):
        q = query_builder.build_delete(name=self.name, filters=filters)
        return self.connection.execute(q)

