from contracting.db.encoder import encode
from contracting import config
from contracting.db.driver import ContractDriver


class ContractDBDriver(ContractDriver):
    def __init__(self, host=config.DB_URL, port=config.DB_PORT, delimiter=config.INDEX_SEPARATOR, db=0,
                 code_key=config.CODE_KEY, type_key=config.TYPE_KEY):
        super().__init__(host, port, delimiter, db, code_key, type_key)

        # Tests if access to the DB is available
        self.sets = {}

    def set(self, key, value):
        self.sets[key] = encode(value)
        super().set(key, value)

    def clear_sets(self):
        self.sets = {}

    def set_contract(self, name, code, owner=None, overwrite=False):
        super().set_contract(name, code, owner, overwrite)
        self.commit()

    def get_key(self, contract, variable, key):
        if key is None:
            response = self.get('{}.{}'.format(contract, variable))
        else:
            response = self.get('{}.{}:{}'.format(contract, variable, key))

        return response
