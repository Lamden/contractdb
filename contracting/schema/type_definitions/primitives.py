import re

from .base import TypeDefinition, InvalidOptionPassed


class String(TypeDefinition):
    @staticmethod
    def validate_options(optional=None, regex=None, length=None):
        super().validate_options(optional)

        if regex is not None:
            try:
                re.compile(regex)
            except re.error:
                raise InvalidOptionPassed

        if length is not None and length < 1:
            raise InvalidOptionPassed


class Int(TypeDefinition):
    @staticmethod
    def validate_options(optional=None, signed=False, bits=None):
        super().validate_options(optional)

        if signed not in [True, False]:
            raise InvalidOptionPassed

        if bits not in [None, 8, 16, 32, 128, 256]:
            raise InvalidOptionPassed


class Number(Int):
    @staticmethod
    def validate_options(optional=None, signed=False, bits=None, precision=64):
        super().validate_options(optional, signed, bits)

        if not 0 <= precision <= 64:
            raise InvalidOptionPassed


class Bool(TypeDefinition):
    @staticmethod
    def validate_options(optional=None):
        super().validate_options(optional)


class Hex(TypeDefinition):
    @staticmethod
    def validate_options(optional=None, bytes=None):
        super().validate_options(optional)

        if bytes is not None and bytes % 2 != 0:
            raise InvalidOptionPassed


class Binary(TypeDefinition):
    @staticmethod
    def validate_options(optional=None, bytes=None):
        super().validate_options()

        if bytes is not None and bytes <= 0:
            raise InvalidOptionPassed


class Date(TypeDefinition):
    @staticmethod
    def validate_options(optional=None):
        super().validate_options(optional)


class Time(TypeDefinition):
    @staticmethod
    def validate_options(optional=None):
        super().validate_options(optional)


class DateTime(TypeDefinition):
    @staticmethod
    def validate_options(optional=None):
        super().validate_options(optional)


class Enum(TypeDefinition):
    @staticmethod
    def validate_options(optional=None, values=None):
        super().validate_options(optional)

        if len(values) != len(set(values)):
            raise InvalidOptionPassed


MAPPING = {
    'string': String,
    'int': Int,
    'number': Number,
    'bool': Bool,
    'hex': Hex,
    'binary': Binary,
    'date': Date,
    'time': Time,
    'datetime': DateTime,
    'enum': Enum
}
