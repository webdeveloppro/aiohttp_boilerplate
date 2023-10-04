import logging
from aiohttp import web
from ..logging.helpers import GCPLogger


# Create logger in request with all info
@web.middleware
async def logger_to_request(request:web.Request, handler):
    log = GCPLogger("request")
    log.setRequest(request)
    request.log = log
    response = await handler(request)
    return response
