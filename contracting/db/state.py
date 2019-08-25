class Connection:
    def execute(self, statement: str):
        raise NotImplementedError


class SpaceStorageDriver:
    def create_space(self, space: str, source_code: str, compiled_code: bytes) -> bool:
        raise NotImplementedError

    def connect_to_space(self, space: str) -> Connection:
        raise NotImplementedError

