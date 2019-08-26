from ...db.orm import Variable, Hash, ForeignVariable, ForeignHash
from ...db.contract import Contract, SQLContract
from ...execution.runtime import rt


class V(Variable):
    def __init__(self, *args, **kwargs):
        if rt.env.get('__Driver') is not None:
            kwargs['driver'] = rt.env.get('__Driver')
        super().__init__(*args, **kwargs)


class H(Hash):
    def __init__(self, *args, **kwargs):
        if rt.env.get('__Driver') is not None:
            kwargs['driver'] = rt.env.get('__Driver')
        super().__init__(*args, **kwargs)


class FV(ForeignVariable):
    def __init__(self, *args, **kwargs):
        if rt.env.get('__Driver') is not None:
            kwargs['driver'] = rt.env.get('__Driver')
        super().__init__(*args, **kwargs)


class FH(ForeignHash):
    def __init__(self, *args, **kwargs):
        if rt.env.get('__Driver') is not None:
            kwargs['driver'] = rt.env.get('__Driver')
        super().__init__(*args, **kwargs)


class C(Contract):
    def __init__(self, *args, **kwargs):
        if rt.env.get('__Driver') is not None:
            kwargs['driver'] = rt.env.get('__Driver')
        super().__init__(*args, **kwargs)


class S(SQLContract):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


# Define the locals that will be available for smart contracts at runtime
exports = {
    'Variable': V,
    'Hash': H,
    'ForeignVariable': FV,
    'ForeignHash': FH,
    '__Contract': C,
    '__SQLContract': S
}