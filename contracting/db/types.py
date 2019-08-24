from functools import partial
from decimal import Decimal


class Type:
    @staticmethod
    def to_raw(obj):
        raise NotImplementedError

    @staticmethod
    def from_raw(data):
        raise NotImplementedError


class Bool(Type):
    @staticmethod
    def to_raw(obj):
        return bool(obj)

    @staticmethod
    def from_raw(data):
        return data


class Int(Type):
    @staticmethod
    def to_raw(obj):
        return int(obj)

    @staticmethod
    def from_raw(data):
        return data


class Text(Type):
    @staticmethod
    def to_raw(obj):
        return str(obj)

    @staticmethod
    def from_raw(data):
        return data


class Blob(Type):
    @staticmethod
    def to_raw(obj):
        return bytes(obj)

    @staticmethod
    def from_raw(data):
        return data


class FixedClassFactory:
    def __call__(self, p):
        return type('Fixed{}'.format(p),
                   (Type,),
                   {'to_raw': partial(self.to_raw, precision=p),
                    'from_raw': partial(self.from_raw, precision=p)
                    })

    @staticmethod
    def to_raw(obj, precision):
        return '{}'.format(round(obj, precision))

    @staticmethod
    def from_raw(data):
        return Decimal(data)


Fixed = FixedClassFactory()
