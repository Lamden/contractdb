from . import filters


class Connection:
    def execute(self, statement: str):
        raise NotImplementedError


class Result:
    def __init__(self, result: bool, connection: Connection):
        self.result = result
        self.connection = connection


class ReadResult(Result):
    def __init__(self, result: bool, connection: Connection):
        super().__init__(result, connection)

    def fetch_one(self):
        raise NotImplementedError

    def fetch_all(self):
        raise NotImplementedError

    def filter(self, filter: filters.Filter) -> Result:
        raise NotImplementedError


class SpaceStorageDriver:
    def create_space(self, space: str, source_code: str, compiled_code: bytes) -> bool:
        raise NotImplementedError

    def connect_to_space(self, space: str) -> Connection:
        raise NotImplementedError

