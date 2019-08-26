import sqlite3
import os

class Connection:
    def execute(self, statement: str):
        raise NotImplementedError


class SpaceStorageDriver:
    def create_space(self, space: str, source_code: str, compiled_code: bytes) -> bool:
        raise NotImplementedError

    def connect_to_space(self, space: str) -> Connection:
        raise NotImplementedError


class ResultSet:
    def fetchone(self) -> dict:
        raise NotImplementedError

    def fetchall(self) -> dict:
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError

    def __next__(self):
        raise NotImplementedError

    def __getitem__(self, item):
        raise NotImplementedError


class SQLConnection(Connection):
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    def execute(self, statement: str):
        self.connection.execute(statement)
        self.connection.commit()


class SQLSpaceStorageDriver(SpaceStorageDriver):
    def __init__(self, root='./'):
        self.root = root

    def create_space(self, space: str, source_code: str, compiled_code: bytes):
        if space.isalpha():
            db = sqlite3.connect('{}{}.db'.format(self.root, space))
            db.execute('create table if not exists contract (source text, compiled blob)')
            db.execute('insert into contract values (?, ?)', source_code, compiled_code)
            db.commit()
            return True
        return False

    def connect_to_space(self, space: str):
        if space.isalpha():
            db = sqlite3.connect('{}{}.db'.format(self.root, space))
            return SQLConnection(connection=db)


class SQLResultSet(ResultSet):
    def __init__(self, cursor: sqlite3.Cursor):
        self.cursor = cursor
        self.retrieved = []
        self.i = 0

    def fetchone(self):
        to_add = self.cursor.fetchone()
        self.retrieved.append(to_add)
        self.i += 1
        return self.retrieved[-1]

    def fetchall(self):
        to_add = self.cursor.fetchall()
        self.retrieved.extend(to_add)
        self.i += len(to_add)
        return self.retrieved

    def __next__(self):
        return self.fetchone()

    def __iter__(self):
        return self

    def __getitem__(self, item):
        if item >= self.i:
            while item >= self.i:
                self.fetchone()
            return self.retrieved[-1]
        else:
            return self.retrieved[item]