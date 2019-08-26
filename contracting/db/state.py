import sqlite3
import os


class Connection:
    def execute(self, statement: str, *args):
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


class SQLResultSet(ResultSet):
    def __init__(self, cursor: sqlite3.Cursor):
        self.cursor = cursor
        self.retrieved = []
        self.i = 0

        self.fully_iterated = False

    def fetchone(self):
        to_add = self.cursor.fetchone()
        if to_add is not None:
            self.retrieved.append(to_add)
            self.i += 1
            return self.retrieved[-1]

        self.fully_iterated = True
        return to_add

    def fetchall(self):
        to_add = self.cursor.fetchall()
        self.retrieved.extend(to_add)
        self.i += len(to_add)
        self.fully_iterated = True
        return self.retrieved

    def __next__(self):
        if self.fully_iterated:
            return next(self.retrieved)

        r = self.fetchone()
        if r is None:
            raise StopIteration
        return r

    def __iter__(self):
        if self.fully_iterated:
            return iter(self.retrieved)

        return self

    def __getitem__(self, item):
        if item >= self.i:
            r = None

            while item >= self.i:
                r = self.fetchone()

                if r is None:
                    raise IndexError

            return r
        else:
            return self.retrieved[item]


class SQLConnection(Connection):
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    def execute(self, statement: str, *args):
        res = self.connection.execute(statement, *args)
        self.connection.commit()
        return SQLResultSet(cursor=res)


class SQLSpaceStorageDriver(SpaceStorageDriver):
    def __init__(self, root=os.path.expanduser('~/contracts/')):
        self.root = root

    def create_space(self, space: str, source_code: str, compiled_code: bytes):
        if space.isalpha():
            db = sqlite3.connect(self.get_path_for_space(space))
            db.execute('create table if not exists contract (source text, compiled blob)')
            db.execute('insert into contract values (?, ?)', (source_code, compiled_code))
            db.commit()
            return True
        return False

    def connect_to_space(self, space: str):
        if space.isalpha():
            db = sqlite3.connect(self.get_path_for_space(space))
            return SQLConnection(connection=db)

    def delete_space(self, space: str):
        if space.isalpha():
            os.remove(self.get_path_for_space(space))

    def source_code_for_space(self, space: str):
        conn = self.connect_to_space(space=space)
        res = conn.execute('select source from contract')
        return res.fetchone()[0]

    def compiled_code_for_space(self, space: str):
        conn = self.connect_to_space(space=space)
        res = conn.execute('select compiled from contract')
        return res.fetchone()[0]

    def get_path_for_space(self, space):
        return os.path.join(self.root, '{}.db'.format(space))