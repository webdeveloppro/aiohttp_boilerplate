import logging
from pythonjsonlogger import jsonlogger
from aiohttp import web
from ..logging.helpers import GCPLogger


# Create logger in request with all info
@web.middleware
async def logger_to_request(request:web.Request, handler):
    log = GCPLogger("request")

    set_json_formatter(log)

    log.setRequest(request)
    request.log = log
    response = await handler(request)
    log.setResponse(response)
    return response

def set_json_formatter(log):
    logHandler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter()
    logHandler.setFormatter(formatter)
    log.addHandler(logHandler)
