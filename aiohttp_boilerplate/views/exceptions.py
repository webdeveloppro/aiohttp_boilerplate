import json
from aiohttp import web

from aiohttp_boilerplate.log import view_logger


# Sugar for transfer json message to string
def JSONHTTPError(message, errorClass=None, headers=None):
    message = json.dumps(message)
    headers = headers or {}
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

    view_logger.warning(f"{errorClass} Msg: {message}")

    return errorClass(text=message, headers=headers)
