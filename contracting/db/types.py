Bool = 'BOOL'
Int = 'INTEGER'
Text = 'TEXT'
Blob = 'BLOB'
Fixed2 = 'DECIMAL(128,2)'
Fixed4 = 'DECIMAL(128,4)'
Fixed6 = 'DECIMAL(128,6)'
Fixed8 = 'DECIMAL(128,8)'
Fixed10 = 'DECIMAL(128,10)'
Fixed12 = 'DECIMAL(128,12)'


class TypeConverter:
    @staticmethod
    def convert(o):
        if type(o) == int:
            return '{}'.format(o)

        elif type(o) == bool:
            return '1' if o else '0'

        elif type(o) == str:
            return '"{}"'.format(o)
