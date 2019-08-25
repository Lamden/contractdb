class Filter:
    def __init__(self, obj1, obj2):
        self.obj1 = obj1
        self.obj2 = obj2

    def repr(self):
        raise NotImplementedError


class Eq(Filter):
    def repr(self):
        return '{} = {}'.format(self.obj1, self.obj2)


class Not(Filter):
    def repr(self):
        return '{} != {}'.format(self.obj1, self.obj2)


class Gt(Filter):
    def repr(self):
        return '{} > {}'.format(self.obj1, self.obj2)


class Gte(Filter):
    def repr(self):
        return '{} >= {}'.format(self.obj1, self.obj2)


class Lt(Filter):
    def repr(self):
        return '{} < {}'.format(self.obj1, self.obj2)


class Lte(Filter):
    def repr(self):
        return '{} <= {}'.format(self.obj1, self.obj2)