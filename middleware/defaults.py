from aiohttp import web, hdrs


# Restrict access for conf['domain'] domain and subdomains only
async def cross_origin_rules(app, handler):
    async def middleware_handler(request):
        allow = ""
        if app.conf.get('DEBUG') >= 1:
            allow = "*"
        else:
            # Allow requests from subdomains
            if request.headers.get('origin', '').count(app.conf['domain']) == 0:
                allow = request.headers.get('scheme', 'https') + "://" + app.conf['domain']
            else:
                allow = request.headers.get('origin', '')

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


@web.middleware
async def erase_header_server(request, handler):
    try:
        response = await handler(request)
    except web.HTTPException as exc:
        response = exc
    except Exception:
        response = web.Response(
            status=500,
            body='{"error":"Something went wrong"}',
            content_type='application/json'
        )
        import traceback
        import sys
        exc_info = sys.exc_info()
        traceback.print_exception(*exc_info)
        del exc_info

    response.headers[hdrs.SERVER] = ''
    return response
