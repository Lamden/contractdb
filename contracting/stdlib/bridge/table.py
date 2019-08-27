from ...db.table import Table
from ...db.filters import Filters
from ...db import types
from ...execution.runtime import rt


class T(Table):
    def __init__(self, *args, **kwargs):
        if rt.env.get('__Driver') is not None:
            kwargs['driver'] = rt.env.get('__Driver')
        super().__init__(*args, **kwargs)

exports = {
    'Table': T,
    'Filters': Filters,
    'types': types
}