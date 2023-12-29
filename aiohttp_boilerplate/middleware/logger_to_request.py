import logging
from aiohttp import web

# Create logger in request with all info
@web.middleware
async def logger_to_request(request:web.Request, handler):
    log = logging.getLogger("aiohttp:server")
    log.setRequest(request)

    if "context" in request:
        log.setContext(request.context)

    request.log = log
    response = await handler(request)
    log.setResponse(response)
    return response