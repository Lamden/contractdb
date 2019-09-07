import yaml
from .type_definitions import primitives


class InvalidTypeDefault(Exception):
    pass


class InvalidSchema(Exception):
    pass


MUTABLE_TOKENS = {'set', 'list', 'tuple'}
REFERENCE_TOKENS = {'local', 'global'}


def is_valid(schema: str):
    d = yaml.load(schema, Loader=yaml.Loader)

    schema = d.get('schema')

    if schema is None:
        raise InvalidSchema

    for k, v in schema.items():
        if k in primitives.MAPPING.keys() | MUTABLE_TOKENS | REFERENCE_TOKENS:
            raise InvalidTypeDefault

        if type(v) == str:
            validate_type_default(v)

        elif type(v) == dict:
            if len(v) == 1:
                validate_type_definition(v)
            else:
                validate_object(v)


def validate_type_default(s: str):
    if s not in primitives.MAPPING.keys():
        raise InvalidTypeDefault


def validate_type_definition(d: dict):
    k, v = list(d.items())[0]

    if k in primitives.MAPPING.keys():
        validator = primitives.MAPPING[k]
        validator.validate_options(**v)

    elif k in MUTABLE_TOKENS:
        pass

    elif k in REFERENCE_TOKENS:
        pass

    else:
        raise InvalidTypeDefault


def validate_object(d: dict):
    for k, v in d.items():
        if k in primitives.MAPPING.keys() | MUTABLE_TOKENS | REFERENCE_TOKENS:
            raise InvalidTypeDefault
