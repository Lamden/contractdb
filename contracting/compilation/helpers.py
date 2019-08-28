from contracting.compilation.compiler import ContractingCompiler
import ast


class CodeHelper:
    def __init__(self, compiler=ContractingCompiler()):
        self.compiler = compiler

    # Parses the AST and returns the variable names for any classes in a set that you pass.
    # Ex: {'Variable', 'Hash'} returns all initializations of those variables. This is used for figuring out what
    # variables you can query against in a piece of code.
    @staticmethod
    def get_variable_names_for_initialized_classes(code: str, classes: set):
        v = []

        tree = ast.parse(code)

        for node in ast.walk(tree):
            if type(node) != ast.Assign:
                continue

            try:
                if type(node.value) is not ast.Call:
                    continue

                if node.value.func.id not in classes:
                    continue

                var_name = node.targets[0].id
                v.append(var_name.lstrip('__'))

            except AttributeError:
                pass

        return v

    # Parses the AST and returns a list of methods with arguments that you can call. You must pass in already compiled
    # code because this method uses the __ privatization method of 'locking off' certain methods from being run via tx.
    # This is used to learn what a smart contract's API is programmatically.
    @staticmethod
    def get_methods_for_compiled_code(code: str):
        tree = ast.parse(code)

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

    # This will return any violations for a piece of code. Same as just linting code, but returns it as a list. You can
    # also use different compilers, if needed in the future.
    def get_violations_for_code(self, code: str):
        tree = ast.parse(code)
        violations = self.compiler.linter.check(tree)

        return_list = []

        for violation in violations:
            return_list.append(violation)

        return return_list
