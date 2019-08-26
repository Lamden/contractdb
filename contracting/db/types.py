from functools import partial
from decimal import Decimal


class Type:
    @staticmethod
    def to_raw(obj):
        raise NotImplementedError

    @staticmethod
    def from_raw(data):
        raise NotImplementedError

    @staticmethod
    def repr():
        raise NotImplementedError


class Bool(Type):
    @staticmethod
    def to_raw(obj):
        return bool(obj)

    @staticmethod
    def from_raw(data):
        return data

    @staticmethod
    def repr():
        return 'BOOL'


class Int(Type):
    @staticmethod
    def to_raw(obj):
        return int(obj)

    @staticmethod
    def from_raw(data):
        return data

    @staticmethod
    def repr():
        return 'INTEGER'


class Text(Type):
    @staticmethod
    def to_raw(obj):
        return str(obj)

    @staticmethod
    def from_raw(data):
        return data

    @staticmethod
    def repr():
        return 'TEXT'


class Blob(Type):
    @staticmethod
    def to_raw(obj):
        return bytes(obj)

    @staticmethod
    def from_raw(data):
        return data

    @staticmethod
    def repr():
        return 'BLOB'


class FixedClassFactory:
    def __call__(self, p):
        return type('Fixed{}'.format(p),
                   (Type,),
                   {'to_raw': partial(self.to_raw, precision=p),
                    'from_raw': partial(self.from_raw, precision=p),
                    'repr': partial(self.repr, precision=p)
                    })

    @staticmethod
    def to_raw(obj, precision):
        return '{}'.format(round(obj, precision))

    @staticmethod
    def from_raw(data):
        return Decimal(data)

    @staticmethod
    def repr(precision):
        return 'DECIMAL(128,{})'.format(precision)


Fixed = FixedClassFactory()
