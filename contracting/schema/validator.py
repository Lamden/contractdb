import yaml
from .type_definitions import primitives


class InvalidTypeDefault(Exception):
    pass


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
    if s not in primitives.MAPPING.keys() | MUTABLE_TOKENS | REFERENCE_TOKENS:
        raise InvalidTypeDefault


def validate_type_definition(d: dict):
    k = list(d.keys())[0]

    if k in primitives.MAPPING.keys():
        validate_primitive_type(d)

    elif k in MUTABLE_TOKENS:
        pass

    elif k in REFERENCE_TOKENS:
        pass

    else:
        raise InvalidTypeDefault


def validate_primitive_type(d: dict):
    pass


def validate_object(d: dict):
    for k, v in d.items():
        if k in PRIMITIVE_MAPPING.keys() | MUTABLE_TOKENS | REFERENCE_TOKENS:
            raise InvalidTypeDefault
