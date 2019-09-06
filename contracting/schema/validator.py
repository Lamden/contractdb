import yaml

PRIMITIVE_TOKENS = {'string', 'int', 'number', 'bool', 'hex', 'binary', 'date', 'time', 'datetime', 'enum'}
MUTABLE_TOKENS = {'set', 'list', 'tuple'}
REFERENCE_TOKENS = {'local', 'global'}


def is_valid(schema: str):
    d = yaml.load(schema)

    if d.get('schema') is None:
        return False


def validate_multi_key_map(d):
    for k, v in d.items():
        if k in PRIMITIVE_TOKENS | MUTABLE_TOKENS | REFERENCE_TOKENS:
            return False
    return True