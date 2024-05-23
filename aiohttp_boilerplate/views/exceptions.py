import json
from aiohttp import web

from aiohttp_boilerplate.logging import get_logger
from aiohttp_boilerplate import config

logger_name = 'aiohttp_boilerplate.views'

logger = get_logger(logger_name)

class JSONHTTPError(web.HTTPClientError):
    def __init__(self, request, message, error_class=web.HTTPBadRequest):
        """ Helper to parse json and return string """
        if request is not None:
            request.log.debug(message)
        self.request = request
        self.status_code = error_class().status_code

        message = json.dumps(message)
        super().__init__(
            text=message,
            content_type='application/json',
        )
