import json
from aiohttp import web

from aiohttp_boilerplate.logging import get_logger

log = get_logger('aiohttp_boilerplate.views')


def JSONHTTPError(message, error_class=None, headers=None):
    """ Helper to parse json and return string """
    message = json.dumps(message)
    headers = headers or {}
    headers['Content-Type'] = 'application/json'

    # ToDo
    # move to middleware
    headers['Access-Control-Allow-Credentials'] = 'true'
    headers['Access-Control-Allow-Origin'] = '*'
    headers['Access-Control-Allow-Methods'] = \
        'GET, POST, PUT, OPTIONS, DELETE, PATCH'
    headers['Access-Control-Allow-Headers'] = \
        'Authorization, X-PINGOTHER, Content-Type, X-Requested-With'

    if error_class is None:
        error_class = web.HTTPBadRequest

    log.debug(message)
    return error_class(text=message, headers=headers)
