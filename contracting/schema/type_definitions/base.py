class InvalidOptionPassed(Exception):
    pass


class TypeDefinition:
    @staticmethod
    def validate_options(optional=None):
        if optional not in [None, True, False]:
            raise InvalidOptionPassed
