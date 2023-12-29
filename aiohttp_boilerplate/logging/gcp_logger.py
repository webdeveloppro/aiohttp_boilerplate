import logging

from aiohttp.web import Request
from aiohttp.web_response import StreamResponse
from pythonjsonlogger import jsonlogger
from datetime import datetime


GCPSeverityMap = {
	logging.DEBUG: "DEBUG",
	logging.INFO:  "INFO",
    logging.WARNING:  "WARNING",
    logging.ERROR:  "ERROR",
	logging.CRITICAL: "CRITICAL",
}

class GCPLogger(logging.Logger):
    request: Request
    response: StreamResponse
    component: str

    def __init__(self, *args, format='json', stack_info=False, stacklevel=3, extra_labels={}, **kwargs):
        super().__init__(*args, **kwargs)
        self.component = ""
        if len(args) > 0:
            self.component = args[0]
        self.request = None
        self.response = None
        self.context = None
        self.default_stack_info = stack_info
        self.default_stacklevel = stacklevel
        self.extra = extra_labels

        if format == "json":
            logHandler = logging.StreamHandler()
            formatter = jsonlogger.JsonFormatter()
            logHandler.setFormatter(formatter)
            self.addHandler(logHandler)

        # self.addFilter(self.add_extra)
            
    def new_component_logger(self, name):
        copy_logger = GCPLogger(name)
        copy_logger.request = self.request
        copy_logger.response = self.response
        copy_logger.context = self.context
        copy_logger.default_stack_info = self.default_stack_info
        copy_logger.default_stacklevel = self.default_stacklevel

        return copy_logger

    def setRequest(self, request: Request):
        self.request = request

    def setResponse(self, response: StreamResponse):
        self.response = response

    def setComponent(self, component: str):
        self.component = component
    
    def addExtra(self, record, level, *args):
        # list of available keys for google cloud
        # google/cloud/logging_v2/handlers/handlers.py,CloudLoggingFilter, func filter
        extra = {
            "component": self.name,
            "serviceContext": {
                **self.extra,
            },
        }
        if len(args) > 0:
            extra["error"] = args[0]
        if self.context and self.context.request_id:
            extra["trace"] = self.context.request_id
        if self.context and self.context.user:
            extra["json_fields"]["user"] = self.context.user
        if self.context and self.context.service_context:
            extra["json_fields"]["serviceContext"] = self.context.service_context
        if self.request:
            extra["serviceContext"]["httpRequest"] = {
                "method": self.request.method,
                "url": self.request.path_qs,
                "userAgent": self.request.headers.get("userAgent", ""),
                "referer": self.request.headers.get("referer", ""),
                # "status": "",
                "remoteIp": self.request.remote,
                # "latency": "",
                "protocol": self.request.scheme
            }
            if self.response and self.response.code:
                extra["serviceContext"]["httpRequest"]["responseStatusCode"] = self.response.code
            # ToDo
            # calculate latency
            # extra["http_request"]["latency"] = ""
        
        # Add severity for GCP monitoring
        extra["severity"] = GCPSeverityMap[level]
        extra["time"] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

        return extra

    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=None,
             stacklevel=None):
        
        if stack_info is None:
            stack_info = self.default_stack_info

        if stacklevel is None:
            stacklevel = self.default_stacklevel

        if extra is None:
            extra = {}

        extra.update(self.addExtra(msg, level, *args))
        args = []
        return super()._log(level, msg, args, exc_info, extra, stack_info, stacklevel)