from contracting.execution.executor import Engine
from contracting import utils
import ast
import struct
from contracting.db.chain import BlockStorageDriver

NO_CONTRACT = 1
NO_VARIABLE = 2


class StateInterface:
    def __init__(self, driver, compiler, engine: Engine, blocks: BlockStorageDriver=None):
        self.driver = driver
        self.compiler = compiler
        self.engine = engine

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
            'compile': self.compile_code
        }

        if self.blocks is not None:
            self.blocks_enabled = True

            self.command_map.update({
                'get_block_by_hash': self.blocks.get_block_by_hash,
                'get_block_by_index': self.blocks.get_block_by_index,
                'block_height': self.blocks.height,
                'block_hash': self.blocks.latest_hash,
            })

    def get_contract(self, name: str):
        code = self.driver.get_contract(name)

        if code is None:
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

        tree = ast.parse(contract_code)

        function_defs = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]

        funcs = []
        for definition in function_defs:
            func_name = definition.name
            kwargs = [arg.arg for arg in definition.args.args]

            if not func_name.startswith('__'):
                funcs.append({
                    'name': func_name,
                    'arguments': kwargs
                })

        return funcs

    def get_var(self, contract: str, variable: str, key: str=None):
        contract_code = self.driver.get_contract(contract)

        if contract_code is None:
            return {
                'status': NO_CONTRACT
            }

        # Multihashes don't work here
        # Make contract self.driver deal with this so we can abstract it later
        response = self.driver.get_key(contract, variable, key)

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

        v = []

        tree = ast.parse(contract_code)

        for node in ast.walk(tree):
            if type(node) != ast.Assign:
                continue

            try:
                if type(node.value) is not ast.Call:
                    continue

                if node.value.func.id not in {'Variable', 'Hash'}:
                    continue

                var_name = node.targets[0].id
                v.append(var_name.lstrip('__'))

            except AttributeError:
                pass

        return v

    def run(self, transaction: dict):
        output = self.engine.run(transaction)
        transaction['index'] = 0
        result = utils.make_finalized_tx(transaction, output)

        if self.blocks_enabled:
            block_hash = bytes.fromhex(self.blocks.latest_hash)
            index_as_bytes = struct.pack('>H', 0)
            encoded_tx_in = utils.hash_dict(transaction)
            encoded_tx_out = utils.hash_dict(output)

            new_tx_hash = utils.hash_bytes(block_hash + index_as_bytes +
                                           encoded_tx_in + encoded_tx_out)

            result['hash'] = new_tx_hash

            stored_block = self.blocks.store_txs([result])
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
                block_hash = bytes.fromhex(self.blocks.latest_hash)
                index_as_bytes = struct.pack('>H', i)
                encoded_tx_in = utils.hash_dict(transaction)
                encoded_tx_out = utils.hash_dict(output)

                new_tx_hash = utils.hash_bytes(block_hash + index_as_bytes +
                                               encoded_tx_in + encoded_tx_out)

                result['hash'] = new_tx_hash

            results.append(result)

        if self.blocks_enabled:
            stored_block = self.blocks.store_txs(results)
            return stored_block

        else:
            return results

    def lint(self, code: str):
        tree = ast.parse(code)
        violations = self.compiler.linter.check(tree)

        return_list = []

        for violation in violations:
            return_list.append(violation)

        return return_list

    def compile_code(self, code: str):
        return self.compiler.parse_to_code(code)

    def process_json_rpc_command(self, payload: dict):
        command = payload.get('command')
        arguments = payload.get('arguments')

        if command is None or arguments is None:
            return

        func = self.command_map.get(command)

        if func is None:
            return

        return func(**arguments)


