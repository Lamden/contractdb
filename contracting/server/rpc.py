from ..db.driver import ContractDriver
from ..execution.executor import Engine
from ..compilation.compiler import ContractingCompiler
from .. import utils

import ast

driver = ContractDriver()
compiler = ContractingCompiler()
engine = Engine()

NO_CONTRACT = 1
NO_VARIABLE = 2


def get_contract(name: str):
    code = driver.get_contract(name)

    if code is None:
        return {
            'status': NO_CONTRACT
        }

    return code


def get_methods(contract: str):
    contract_code = driver.get_contract(contract)

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


def get_var(contract: str, variable: str, key: str=None):
    contract_code = driver.get_contract(contract)

    if contract_code is None:
        return {
            'status': NO_CONTRACT
        }

    # Multihashes don't work here
    # Make contract driver deal with this so we can abstract it later
    if key is None:
        response = driver.get('{}.{}'.format(contract, variable))
    else:
        response = driver.get('{}.{}:{}'.format(contract, variable, key))

    if response is None:
        return {
            'status': NO_VARIABLE
        }

    return response


def get_vars(contract: str):
    contract_code = driver.get_contract(contract)

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


def run(transaction: dict):
    output = engine.run(transaction)
    return utils.make_finalized_tx(transaction, output)


def run_all(transactions: list):
    results = []

    for transaction in transactions:
        output = engine.run(transaction)
        result = utils.make_finalized_tx(transaction, output)
        results.append(result)

    return results


def lint(code: str):
    tree = ast.parse(code)
    violations = compiler.linter.check(tree)

    return_list = []

    for violation in violations:
        return_list.append(violation)

    return return_list


def compile_code(code: str):
    return compiler.parse_to_code(code)


# String to callable map for strict RPC capabilities. Explicit for a reason!
command_map = {
    'get_contract': get_contract,
    'get_var': get_var,
    'get_vars': get_vars,
    'run': run,
    'run_all': run_all,
    'lint': lint,
    'compile': compile_code
}


# Single function call to map RPC command to an actual Python function. Allows the server to just call this.
def process_json_rpc_command(payload: dict):
    command = payload.get('command')
    arguments = payload.get('arguments')

    if command is None or arguments is None:
        return

    func = command_map.get(command)

    if func is None:
        return

    return func(**arguments)
