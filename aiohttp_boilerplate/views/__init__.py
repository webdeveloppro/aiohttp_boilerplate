import datetime
import decimal
import json
import types
from functools import partial

from .exceptions import JSONHTTPError
from .request import Context

# JSON serialization tuning
# Fix for datetime, decimal, memoryview and bytes type
def fix_json(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    # ToDo
    # should we install python-dateutils
    # Or just use this hack ?
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    if isinstance(obj, datetime.date):
        return obj.isoformat()
    if type(obj) == memoryview:
        return bytes(obj)
    if isinstance(obj, types.MethodType):
        return obj()
    raise TypeError('unknown type: ', type(obj), obj)


fixed_dump = partial(json.dumps, indent=None, default=fix_json)

__all__ = ('JSONHTTPError', 'Context', 'fixed_dump', )
