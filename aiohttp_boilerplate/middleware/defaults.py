import logging
from aiohttp import web, hdrs


# Restrict access for conf['domain'] domain and subdomains only
@web.middleware
async def cross_origin_rules(request, handler):

    # Allow requests from subdomains
    domain = request.app.conf.get('domain', '')
    allow = f"{request.headers.get('scheme', 'https')}://{domain}"
    origin = str(request.headers.get('origin', ''))
    if origin.count(domain) > 0:
        allow = origin

    response = await handler(request)
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Origin'] = allow
    response.headers['Access-Control-Allow-Methods'] = \
        'GET, POST, PUT, OPTIONS, DELETE, PATCH'
    response.headers['Access-Control-Allow-Headers'] = \
        'Authorization, X-PINGOTHER, Content-Type, X-Requested-With, X-Request-ID, Vary'

    return response


# Return status: 200 response for /status200 url
@web.middleware
async def url_status_200(request, handler):
    if request.raw_path == '/healthcheck':
        response = web.Response(text="Ok")
    else:
        response = await handler(request)
    return response

# Remove server info
@web.middleware
async def erase_header_server(request, handler):
    response = await handler(request)
    response.headers[hdrs.SERVER] = ''
    return response
