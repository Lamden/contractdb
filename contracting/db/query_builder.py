def build_parenthesis(i):
    s = '('
    for i in range(i - 1):
        s += '?, '
    s += '?)'

    return s


def build_insert_into(name, values):
    parenthesis = build_parenthesis(values)
    s = 'INSERT INTO {} VALUES {};'.format(name, parenthesis)
    return s


def build_create_table_query(name, values):
    q = 'CREATE TABLE IF NOT EXISTS {} '.format(name)

    q += '('
    for k, v in values.items():
        q += '{} {}, '.format(k, v)
    q = q[:-2]

    q += ');'

    return q


def build_where(filters=[]):
    s = ''
    if len(filters) > 0:
        s += 'WHERE '
        for f in filters:
            s += f
            s += ' AND '
        s = s[:-5]

    return s


def build_select(columns={}, name=None, filters=[]):
    s = 'SELECT '

    if len(columns) == 0:
        s += '*'

    else:
        for c in columns:
            s += '{}, '.format(c)
        s = s[:-2]

    s += ' FROM {}'.format(name)
    s += ' {}'.format(build_where(filters))

    if s[-1] == ' ':
        s = s[:-1]

    s += ';'

    return s


def build_update(name, sets={}, filters=[]):
    q = 'UPDATE {} SET '.format(name)

    for k, v in sets.items():
        q += '{} = {} AND '.format(k, v)
    q = q[:-5]

    q += ' {}'.format(build_where(filters))

    if q[-1] == ' ':
        q = q[:-1]

    q += ';'

    return q