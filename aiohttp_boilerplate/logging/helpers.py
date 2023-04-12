import aiohttp.web_log as aio_helpers
from aiohttp.web_request import BaseRequest
from aiohttp.web_response import StreamResponse



class NoHeathCheckLogs(aio_helpers.AccessLogger):
    def log(self, request: BaseRequest, response: StreamResponse, time: float) -> None:
        if request and request.rel_url == "/healthcheck":
            # Do not log healthcheck requests
            return
        super().log(request, response, time)
