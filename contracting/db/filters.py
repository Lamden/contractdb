class Filter:
    def __init__(self, obj1, obj2):
        self.obj1 = obj1
        self.obj2 = obj2


class Eq(Filter):
    pass


class Not(Filter):
    pass


class Gt(Filter):
    pass


class Gte(Filter):
    pass


class Lt(Filter):
    pass


class Lte(Filter):
    pass
