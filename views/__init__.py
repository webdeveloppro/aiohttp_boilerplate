import datetime
import decimal
import sys
import json
import types

from functools import partial


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
    print('unknown type: ', type(obj), obj, file=sys.stderr)
    raise TypeError


fixed_dump = partial(json.dumps, indent=None, default=fix_json)
