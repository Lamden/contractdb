from contracting.db.chain import BlockStorageDriver

SUCCESS = 0
BAD_ARG = 1
NO_BLOCK = 2
NO_TX = 3


class BlockInterface:
    def __init__(self, driver: BlockStorageDriver):
        self.driver = driver

        self.command_map = {
            'get_block': self.get_block,
            'get_tx': self.get_tx,
            'store_txs': self.store_txs,
        }

    def get_block(self, hash_or_num):
        if type(hash_or_num) == str:
            block = self.driver.get_block_by_hash(hash_or_num)

        elif type(hash_or_num) == int:
            block = self.driver.get_block_by_index(hash_or_num)

        else:
            return {
                'status': BAD_ARG
            }

        if block is None:
            return {
                'status': NO_BLOCK
            }

        return block

    def get_tx(self, h: str):
        tx = self.driver.get_transaction_by_hash(h)

        if tx is None:
            return {
                'status': NO_TX
            }

        return tx

    def store_txs(self, transactions):
        pass