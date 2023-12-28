import uuid

from aiohttp import web
from ..views import Context

REQUEST_ID_HEADER_SETTING = "X-Request-Id"
GENERATE_REQUEST_ID = True

def generate_id():
    return uuid.uuid4().hex

def get_request_id(request:web.Request):
    request_id = request.headers.get(REQUEST_ID_HEADER_SETTING, None)
    if not request_id and GENERATE_REQUEST_ID:
        request_id = generate_id()
    return request_id

# Get or add request id to the request
@web.middleware
async def x_request_id(request:web.Request, handler):
    if "context" not in request:
        request.context = Context
    request.context.request_id = get_request_id(request)
    response = await handler(request)
    return response
