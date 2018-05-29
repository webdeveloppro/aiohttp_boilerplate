import json
from aiohttp import web


# Sugar for transfer json message to string
def JSONHTTPError(message, errorClass=None, headers={}):
    message = json.dumps(message)
    headers['Content-Type'] = 'application/json'

    # ToDo
    # Run middlewares
    headers['Access-Control-Allow-Origin'] = '*'
    headers['Access-Control-Allow-Methods'] = \
        'GET, POST, PUT, OPTIONS, DELETE, PATCH'
    headers['Access-Control-Allow-Headers'] = \
        'Authorization, X-PINGOTHER, Content-Type, X-Requested-With'

    if errorClass is None:
        errorClass = web.HTTPBadRequest

    return errorClass(body=message, headers=headers)
