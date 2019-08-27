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
    res = t.select(filters=[Filters.eq('hello', i)])

    return res.fetchone()

@export
def delete(i):
    t.delete(filters=[Filters.eq('hello', i)])

@export
def update(i, j):
    t.update(sets={
        'there': j
    }, filters=[Filters.eq('hello', i)])