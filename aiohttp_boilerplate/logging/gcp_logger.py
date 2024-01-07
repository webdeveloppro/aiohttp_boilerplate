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
        logHandler = logging.StreamHandler()

        if format == "json":
            formatter = jsonlogger.JsonFormatter()
            logHandler.setFormatter(formatter)

        self.addHandler(logHandler)
            
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
    
    def addExtra(self, record, level, extra_args, *args):
        # list of available keys for google cloud
        # google/cloud/logging_v2/handlers/handlers.py,CloudLoggingFilter, func filter
        extra = {
            "component": self.name,
            "serviceContext": {
                **self.extra,
                **extra_args,
            },
        }
        if len(args) > 0:
            if level > logging.INFO:
                extra["error"] = args[0]
            else:
                extra["info"] = args[0]
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
                "userAgent": self.request.headers.get("User-Agent", ""),
                "referer": self.request.headers.get("referer", ""),
                # "status": "",
                "remoteIp": self.request.remote,
                # "latency": "",
                "protocol": self.request.scheme
            }
            if self.response and self.response.code:
                extra["serviceContext"]["httpRequest"]["responseStatusCode"] = self.response.code

        # Formatter for aiohttp access_logs https://docs.aiohttp.org/en/v3.7.4.post0/logging.html#access-logs
        if self.component == "access_log":
            extra["serviceContext"] = {}
            first_request_line = extra_args.get("first_request_line", "").split()
            
            if len(first_request_line) >= 3:
                extra["serviceContext"]["httpRequest"] = {
                    "method": first_request_line[0],
                    "url": first_request_line[1],
                    "protocol": first_request_line[2],
                    "userAgent": extra_args.get("request_header", {}).get("User-Agent", ""),
                    "referer": extra_args.get("request_header", {}).get("Referer", ""),
                    "remoteIp": extra_args.get("remote_address"),
                    "response_status": extra_args.get("response_status"),
                    "response_size": extra_args.get("response_size"),
                    # ToDo
                    # calculate latency
                    # "request_latency": "",
                    "request_start_time": extra_args.get("request_start_time"),
                }
        
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

        extra = self.addExtra(msg, level, extra, *args)
        args = []
        return super()._log(level, msg, args, exc_info, extra, stack_info, stacklevel)