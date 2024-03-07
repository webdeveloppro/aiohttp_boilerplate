import json
from aiohttp import web

from aiohttp_boilerplate.logging import get_logger

log = get_logger('aiohttp_boilerplate.views')


def JSONHTTPError(message, error_class=None, headers=None, request=None):
    """ Helper to parse json and return string """
    message = json.dumps(message)
    headers = headers or {}
    headers['Content-Type'] = 'application/json'

    if request is not None:
        domain = request.app.conf.get('domain', '')
        allow = f"{request.headers.get('scheme', 'https')}://{domain}"
        origin = str(request.headers.get('origin', ''))
        if origin.count(domain) > 0:
            headers['Access-Control-Allow-Origin'] = origin
        else:
            headers['Access-Control-Allow-Origin'] = allow

    # ToDo
    # move to middleware
    headers['Access-Control-Allow-Credentials'] = 'true'
    headers['Access-Control-Allow-Methods'] = \
        'GET, POST, PUT, OPTIONS, DELETE, PATCH, X-Request-ID'
    headers['Access-Control-Allow-Headers'] = \
        'Authorization, X-PINGOTHER, Content-Type, X-Requested-With'

    if error_class is None:
        error_class = web.HTTPBadRequest

    log.debug(message)
    return error_class(text=message, headers=headers)
