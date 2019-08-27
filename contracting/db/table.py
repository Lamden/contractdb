from . import filters
from . import state


class Table:
    def __init__(self, contract, name, driver: state.Driver, schema):
        self.contract = contract
        self.name = name
        self._driver = driver
        self._driver.create_table(contract, name, schema)

    # CRUD
    def insert(self, obj: dict) -> state.ResultSet:
        return self._driver.insert(self.contract, self.name, obj)

    def select(self, columns: set, filters: filters.Filter) -> state.ResultSet:
        return self._driver.select(self.contract, self.name, columns, filters)

    def update(self, sets: dict, filters: filters.Filter) -> state.ResultSet:
        return self._driver.update(self.contract, self.name, sets, filters)

    def delete(self, filters: filters.Filter) -> state.ResultSet:
        return self._driver.delete(self.contract, self.name, filters)

