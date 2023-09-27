import logging

from aiohttp.web import Request
from aiohttp.web_response import StreamResponse


class GCPLogger(logging.Logger):
    request: Request
    response: StreamResponse
    component: str

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.component = ""
        self.request = None
        self.response = None
        self.context = None
        # self.addFilter(self.skip_healtcheck)
        # self.addFilter(self.add_extra)

    def setRequest(self, request: Request):
        self.request = request

    def setResponse(self, response: StreamResponse):
        self.response = response

    def setComponent(self, component: str):
        self.component = component

    def skipHealtcheck(self, record) -> bool:
        # Do not log healthcheck requests
        if self.request and str(self.request.rel_url) == "/healthcheck":
            return False
        return True
    
    def addExtra(self, record):
        
        comment = "custom developer comment"
        # list of available keys for google cloud
        # google/cloud/logging_v2/handlers/handlers.py,CloudLoggingFilter, func filter
        extra = {
            # "type_": "type.googleapis.com/google.devtools.clouderrorreporting.v1beta1.ReportedErrorEvent",
            "json_fields": {
                "component": self.component,
                "error": comment,
            },
        }
        if self.context and self.context.request_id:
            extra["trace"] = self.context.request_id
        if self.context and self.context.user:
            extra["json_fields"]["user"] = self.context.user
        if self.context and self.context.service_context:
            extra["json_fields"]["serviceContext"] = self.context.service_context
        if self.request:
            extra["http_request"] = {
                "requestMethod": self.request.method,
                "requestUrl": self.request.path_qs,
                "userAgent": self.request.headers.get("userAgent", ""),
                "referer": self.request.headers.get("referer", ""),
                # "status": "",
                "remoteIp": self.request.remote,
                # "latency": "",
                "protocol": self.request.scheme
            }
            if self.response and self.response.code:
                extra["http_request"]["status"] = self.response.code
            # ToDo
            # calculate latency
            # extra["http_request"]["latency"] = ""
        return extra

    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False,
             stacklevel=1):
        if extra is None:
            extra = {}
        extra.update(self.addExtra(msg))
        return super()._log(level, msg, args, exc_info, extra, stack_info, stacklevel)
