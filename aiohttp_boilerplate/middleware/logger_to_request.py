from aiohttp import web
from aiohttp_boilerplate.logging import get_logger


# Create logger in request with all info
@web.middleware
async def logger_to_request(request:web.Request, handler):
    log = get_logger("request")
    log.setRequest(request)

    request.log = log
    response = await handler(request)
    log.setResponse(response)
    return response