from .base import TypeDefinition, InvalidOptionPassed


class Local(TypeDefinition):
    @staticmethod
    def validate_options(optional=None):
        pass

class Global:
    pass


MAPPING = {
    'local': Local,
    'global': Global
}