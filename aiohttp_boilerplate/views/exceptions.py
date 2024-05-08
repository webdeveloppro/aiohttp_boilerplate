import json
from aiohttp import web

from aiohttp_boilerplate.logging import get_logger
from aiohttp_boilerplate import config

component_name = 'aiohttp_boilerplate.views'

logger = get_logger(component_name)

def JSONHTTPError(message, error_class=None, headers=None, request=None):
    """ Helper to parse json and return string """
    log = logger
    if request is not None:
        log = request.log
        log.set_component_name(component_name)

    message = json.dumps(message)
    headers = headers or {}
    headers['Content-Type'] = 'application/json'

    domain = config.conf.get('domain', '')
    if request is not None:
        allow = f"{request.headers.get('scheme', 'https')}://{domain}"
        origin = str(request.headers.get('origin', ''))
        if origin.count(domain) > 0:
            headers['Access-Control-Allow-Origin'] = origin
        else:
            headers['Access-Control-Allow-Origin'] = allow
    else:
        headers['Access-Control-Allow-Origin'] = domain

    # ToDo
    # move to middleware
    headers['Access-Control-Allow-Credentials'] = 'true'
    headers['Access-Control-Allow-Methods'] = \
        'GET, POST, PUT, OPTIONS, DELETE, PATCH'
    headers['Access-Control-Allow-Headers'] = \
        'Authorization, X-PINGOTHER, Content-Type, X-Requested-With, X-Request-ID, Vary'

    if error_class is None:
        error_class = web.HTTPBadRequest

    request.log.debug(message)
    return error_class(text=message, headers=headers)
