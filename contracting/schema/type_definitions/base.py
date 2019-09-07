class InvalidOptionPassed(Exception):
    pass


class TypeDefinition:
    def validate_options(self, optional=None):
        if optional not in [None, True, False]:
            raise InvalidOptionPassed
