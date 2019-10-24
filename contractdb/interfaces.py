from contractdb.engine import Engine
from contractdb.chain import BlockStorageDriver
from contractdb.helpers import CodeHelper
from contractdb import utils

import struct
import logging

NO_CONTRACT = 1
NO_VARIABLE = 2


class StateInterface:
    def __init__(self, driver, compiler, engine: Engine, blocks: BlockStorageDriver=None):
        self.driver = driver
        self.compiler = compiler
        self.engine = engine

        self.helper = CodeHelper(compiler=self.compiler)

        # Set the engine driver
        self.engine.driver = self.driver

        # Optional interface into block storage
        self.blocks = blocks
        self.blocks_enabled = False

        self.command_map = {
            'get_contract': self.get_contract,
            'get_var': self.get_var,
            'get_vars': self.get_vars,
            'run': self.run,
            'run_all': self.run_all,
            'lint': self.lint,
            'compile': self.compile_code,
            'ping': self.ok
        }

        if self.blocks is not None:
            self.blocks_enabled = True

            self.command_map.update({
                'get_block_by_hash': self.blocks.get_block_by_hash,
                'get_block_by_index': self.blocks.get_block_by_index,
                'block_height': self.blocks.height,
                'block_hash': self.blocks.latest_hash,
            })

        self.log = logging.getLogger('StateInterface')

    def ok(self):
        return {'result': 'ok'}

    def get_contract(self, name: str):
        code = self.driver.get_contract(name)

        if code is None:
            self.log.error("contract with the name '{}' is not found".format(name))
            return {
                'status': NO_CONTRACT
            }

        return code

    def get_methods(self, contract: str):
        contract_code = self.driver.get_contract(contract)

        if contract_code is None:
            return {
                'status': NO_CONTRACT
            }

        funcs = self.helper.get_methods_for_compiled_code(contract_code)

        return funcs

    def get_var(self, contract: str, variable: str, key: list=None):
        contract_code = self.driver.get_contract(contract)

        if contract_code is None:
            return {
                'status': NO_CONTRACT
            }

        if key is not None:
            key = [key] if type(key) is not list else key
        else:
            key = []

        k = self.driver.make_key(key=contract, field=variable, args=key)

        response = self.driver.get(k)

        if response is None:
            return {
                'status': NO_VARIABLE
            }

        return response

    def get_vars(self, contract: str):
        contract_code = self.driver.get_contract(contract)

        if contract_code is None:
            return {
                'status': NO_CONTRACT
            }

        return self.helper.get_variable_names_for_initialized_classes(contract_code, classes={'Variable', 'Hash'})

    def run(self, transaction: dict):
        output = self.engine.run(transaction)
        transaction['index'] = 0
        result = utils.make_finalized_tx(transaction, output)

        if self.blocks_enabled:
            block_hash = bytes.fromhex(self.blocks.latest_hash())
            index_as_bytes = struct.pack('>H', 0)
            encoded_tx_in = utils.hash_dict(transaction)
            encoded_tx_out = utils.hash_dict(output)

            new_tx_hash = utils.hash_bytes(block_hash + index_as_bytes +
                                           encoded_tx_in + encoded_tx_out)

            result['hash'] = new_tx_hash

            stored_block = self.blocks.store_txs([result])

            self.log.debug("Stored new block with hash '{}'".format(new_tx_hash))

            self.engine.driver.latest_hash = self.blocks.latest_hash()
            self.engine.driver.height = self.blocks.height()

            return stored_block
        else:
            return result

    def run_all(self, transactions: list):
        results = []

        for i in range(len(transactions)):
            transaction = transactions[i]

            # Add index for ordering purposes
            transaction['index'] = i

            output = self.engine.run(transaction, part_of_batch=True)

            result = utils.make_finalized_tx(transaction, output)

            # Create a TX Hash that is entirely unique. If not enabled, this will have to be done by another system
            # that is storing the block data.
            if self.blocks_enabled:
                block_hash = bytes.fromhex(self.blocks.latest_hash())
                index_as_bytes = struct.pack('>H', i)
                encoded_tx_in = utils.hash_dict(transaction)
                encoded_tx_out = utils.hash_dict(output)

                new_tx_hash = utils.hash_bytes(block_hash + index_as_bytes +
                                               encoded_tx_in + encoded_tx_out)

                result['hash'] = new_tx_hash

            results.append(result)

        if self.blocks_enabled:
            stored_block = self.blocks.store_txs(results)

            self.log.debug("Stored new blocks for {} transactions".format(len(transactions)))

            self.engine.driver.latest_hash = self.blocks.latest_hash()
            self.engine.driver.height = self.blocks.height()

            return stored_block

        else:
            return results

    def lint(self, code: str):
        a = self.helper.get_violations_for_code(code)
        print(a)
        return self.helper.get_violations_for_code(code)

    def compile_code(self, code: str):
        return self.compiler.parse_to_code(code)

    def process_json_rpc_command(self, payload: dict):
        command = payload.get('command')
        print('cmd ->',command)
        arguments = payload.get('arguments')
        print('args ->', arguments)

        if command is None:
            print('COMMAND IS NONE')
            self.log.error("No command provided with the payload {}".format(payload))
            return

        if arguments is None:
            print('ARGS IS NONE')
            self.log.error("No argument provided for the command {}".format(command))
            return

        func = self.command_map.get(command)

        if func is None:
            print('FUNC IS NONE')
            self.log.error("No method found to execute the command {}".format(command))
            return

        result = func(**arguments)

        return result
