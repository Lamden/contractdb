from .types import TypeConverter


class Filters:
    @staticmethod
    def eq(column, obj):
        return '{} = {}'.format(column, TypeConverter.convert(obj))

    @staticmethod
    def ne(column, obj):
        return '{} != {}'.format(column, TypeConverter.convert(obj))

    @staticmethod
    def gt(column, obj):
        return '{} > {}'.format(column, TypeConverter.convert(obj))

    @staticmethod
    def gte(column, obj):
        return '{} >= {}'.format(column, TypeConverter.convert(obj))

    @staticmethod
    def lt(column, obj):
        return '{} < {}'.format(column, TypeConverter.convert(obj))

    @staticmethod
    def lte(column, obj):
        return '{} <= {}'.format(column, TypeConverter.convert(obj))
