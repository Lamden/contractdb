import sqlite3
import os
import shutil
from . import query_builder
from .filters import Filters
import marshal

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


class Connection:
    def execute(self, statement: str, *args):
        raise NotImplementedError


class ContractStorageDriver:
    def __init__(self, root: str):
        self.root = root
        os.mkdir(self.root)

    def create_contract_space(self, space: str, source_code: str, compiled_code: bytes) -> bool:
        raise NotImplementedError

    def connect_to_contract_space(self, space: str) -> Connection:
        raise NotImplementedError


class Driver:
    def insert(self, contract, name, obj: dict) -> ResultSet:
        raise NotImplementedError

    def select(self, contract, name, columns: set={}, filters=[]) -> ResultSet:
        raise NotImplementedError

    def update(self, contract, name, sets: dict, filters=[]) -> ResultSet:
        raise NotImplementedError

    def delete(self, contract, name, filters=[]) -> ResultSet:
        raise NotImplementedError

    def create_table(self, contract, name, values):
        raise NotImplementedError


class SQLDriver:
    def __init__(self):
        self.storage = SQLContractStorageDriver()
        self.sets = []

    def insert(self, contract, name, obj: dict) -> ResultSet:
        conn = self.storage.connect_to_contract_space(contract)
        q = query_builder.build_insert_into(name, obj)
        self.sets.append((q, obj))
        return conn.execute(q, obj)

    def select(self, contract, name, columns: set={}, filters=[]) -> ResultSet:
        conn = self.storage.connect_to_contract_space(contract)
        q = query_builder.build_select(name=name, columns=columns, filters=filters)
        self.sets.append(q)
        return conn.execute(q)

    def update(self, contract, name, sets: dict, filters=[]) -> ResultSet:
        conn = self.storage.connect_to_contract_space(contract)
        q = query_builder.build_update(name=name, sets=sets, filters=filters)
        self.sets.append(q)
        return conn.execute(q)

    def delete(self, contract, name, filters=[]) -> ResultSet:
        conn = self.storage.connect_to_contract_space(contract)
        q = query_builder.build_delete(name=name, filters=filters)
        self.sets.append(q)
        return conn.execute(q)

    def create_table(self, contract, name, values):
        conn = self.storage.connect_to_contract_space(contract)
        q = query_builder.build_create_table_query(name=name, values=values)
        self.sets.append(q)
        return conn.execute(q)

    def clear_sets(self):
        self.sets = []

    def get_contract(self, contract_name: str):
        return self.storage.source_code_for_space(contract_name)

    def get_key(self, contract, variable, key):
        # Find the primary key of the table to query against
        conn = self.storage.connect_to_contract_space(contract)
        cur = conn.execute('pragma table_info("{}")'.format(variable))

        # The column tuple ends in 0 if not primary, 1 if it does. 2nd element of the array is the name of the column.
        columns = cur.fetchall()
        primary_key = None
        for c in columns:
            if c[-1] == 1:
                primary_key = c[1]
                break

        response = None
        if primary_key is not None:
            cur = self.select(contract=contract, name=variable, filters=[Filters.eq(primary_key, key)])
            response = cur.fetchone()

        return response

    def flush(self):
        if os.path.isdir(self.storage.root):
            shutil.rmtree(self.storage.root)
        os.mkdir(self.storage.root)

    def set_contract(self, name, code, *args, **kwargs):
        code_obj = compile(code, '', 'exec')
        code_blob = marshal.dumps(code_obj)

        self.storage.create_contract_space(name, source_code=code, compiled_code=code_blob)

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


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class SQLContractStorageDriver(ContractStorageDriver):
    def __init__(self, root=os.path.expanduser('~/contracts/')):
        self.root = root

    def create_contract_space(self, space: str, source_code: str, compiled_code: bytes):
        db = sqlite3.connect(self.get_path_for_space(space))
        db.execute('create table if not exists contract (source text, compiled blob)')
        db.execute('insert into contract values (?, ?)', (source_code, compiled_code))
        db.commit()
        return True

    def connect_to_contract_space(self, space: str):
        db = sqlite3.connect(self.get_path_for_space(space))
        db.row_factory = dict_factory
        return SQLConnection(connection=db)

    def delete_space(self, space: str):
        os.remove(self.get_path_for_space(space))

    def source_code_for_space(self, space: str):
        conn = self.connect_to_contract_space(space=space)
        res = conn.execute('select source from contract')
        return res.fetchone()['source']

    def compiled_code_for_space(self, space: str):
        conn = self.connect_to_contract_space(space=space)
        res = conn.execute('select compiled from contract')
        return res.fetchone()['compiled']

    def get_path_for_space(self, space):
        return os.path.join(self.root, '{}.db'.format(space))