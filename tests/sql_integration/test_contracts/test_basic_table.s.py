t = Table(schema={
    'hello': types.Int,
    'there': types.Text
})

@export
def insert(i, j):
    t.insert({
        'hello': i,
        'there': j
    })

@export
def select(i):
    t.select(filters=[Filters.eq('hello', i)])

    return t.fetchone()
