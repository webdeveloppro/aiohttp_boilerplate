from aiohttp import web


# Restrict access for conf['domain'] domain and subdomains only
async def cross_origin_rules(app, handler):
    async def middleware_handler(request):
        allow = ""
        if app.conf.get('DEBUG') >= 1:
            allow = "*"
        else:
            if request.headers.get('origin', '').count(app.conf['domain']) == 0:
                allow = "https://" + app.conf['domain']
            else:
                allow = request.headers.get('origin')
                if allow.startswith('http:/'):
                    allow = allow.replace('http:', 'https:')

        response = await handler(request)
        response.headers['Access-Control-Allow-Origin'] = allow
        response.headers['Access-Control-Allow-Methods'] = \
            'GET, POST, PUT, OPTIONS, DELETE, PATCH'
        response.headers['Access-Control-Allow-Headers'] = \
            'Authorization, X-PINGOTHER, Content-Type, X-Requested-With'

        return response
    return middleware_handler


# Return status: 200 response for /status200 url
async def url_status_200(app, handler):
    async def middleware_handler(request):
        if request.raw_path == '/healthcheck':
            response = web.Response(text="Ok")
        else:
            response = await handler(request)
        return response
    return middleware_handler
