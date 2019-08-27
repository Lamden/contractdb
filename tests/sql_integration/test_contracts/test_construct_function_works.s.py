t = Table(schema={
    'key': types.Text,
    'value': types.Text
})

@export
def get():
    res = t.select(filters=[Filters.eq('key', 'test')])
    return res.fetchone()

@construct
def seed():
    t.insert({'key': 'test', 'value': 42})
