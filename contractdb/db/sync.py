from contractdb.db.driver import ContractDBDriver
from contractdb.db.chain import BlockStorageDriver

# Will execute just the updates for each transaction
def quick_sync_state(block_driver: BlockStorageDriver, state_driver: ContractDBDriver):
    while block_driver.height() > state_driver.height:
        block = block_driver.get_block_by_index(state_driver.height + 1)

# Will fully execute all transactions in the blockchain
def full_sync_state():
    pass
