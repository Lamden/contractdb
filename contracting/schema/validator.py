import yaml


class InvalidTypeDefault(Exception):
    pass


PRIMITIVE_TOKENS = {'string', 'int', 'number', 'bool', 'hex', 'binary', 'date', 'time', 'datetime', 'enum'}
MUTABLE_TOKENS = {'set', 'list', 'tuple'}
REFERENCE_TOKENS = {'local', 'global'}


def is_valid(schema: str):
    d = yaml.load(schema)

    schema = d.get('schema')

    if schema is None:
        return False

    for k, v in schema.items():
        if type(v) == str:
            validate_type_default(v)

        elif type(v) == dict:
            if len(v) == 1:
                validate_type_definition(v)
            else:
                validate_object(v)


def validate_type_default(s: str):
    if s not in PRIMITIVE_TOKENS | MUTABLE_TOKENS | REFERENCE_TOKENS:
        raise InvalidTypeDefault


def validate_type_definition(d: dict):
    return True


def validate_object(d: dict):
    return True

