import datetime
import decimal
import json
import types
from functools import partial

from .exceptions import JSONHTTPError
from .request import Context

# JSON serialization tuning
def fix_json(obj):
    from .. import models
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
    if isinstance(obj, models.Manager):
        return obj.data
    raise TypeError('unknown type: ', type(obj), obj)


fixed_dump = partial(json.dumps, indent=None, default=fix_json)

__all__ = ('JSONHTTPError', 'Context', 'fixed_dump', )
