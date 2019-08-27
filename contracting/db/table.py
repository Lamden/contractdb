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

    def select(self, columns: set={}, filters=[]) -> state.ResultSet:
        return self._driver.select(self.contract, self.name, columns, filters)

    def update(self, sets: dict, filters=[]) -> state.ResultSet:
        return self._driver.update(self.contract, self.name, sets, filters)

    def delete(self, filters=[]) -> state.ResultSet:
        return self._driver.delete(self.contract, self.name, filters)


class ForeignTable:
    def __init__(self, contract, name, driver: state.Driver):
        self.contract = contract
        self.name = name
        self._driver = driver

    def select(self, columns: set = {}, filters=[]) -> state.ResultSet:
        return self._driver.select(self.contract, self.name, columns, filters)
