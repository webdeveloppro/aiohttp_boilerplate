import logging
from pythonjsonlogger import jsonlogger
from aiohttp.abc import AbstractAccessLogger
from .gcp_logger import GCPSeverityMap

# Return true if you need write given request to access logs
def filerRequestsLogs(record) -> bool:
    return record.serviceContext["httpRequest"]["path"] not in ("/healthcheck", "/metrics")

class AccessLoggerRequestResponse(AbstractAccessLogger):
    def __init__(self, logger: logging.Logger, log_format: str) -> None:
        super().__init__(logger, log_format=log_format)
        self.logger.addFilter(filerRequestsLogs)
        self.logger.setLevel(logging.DEBUG)

        logHandler = logging.StreamHandler()
        formatter = jsonlogger.JsonFormatter()
        logHandler.setFormatter(formatter)

        self.logger.addHandler(logHandler)

    def log(self, request, response, time):
        message = {
            "component": "access-log",
            "severity": GCPSeverityMap[logging.INFO],
            "serviceContext": {
                "httpRequest": {
                    "method": request.method,
                    "url": request.path_qs,
                    "path": request.path,
                    "userAgent": request.headers.get("User-Agent", ""),
                    "referer": request.headers.get("referer", ""),
                    "responseStatusCode": response.status,
                    "remoteIp": request.remote,
                    "latency": time,
                    "protocol": request.scheme,
                }
            }
        }
        if "context" in request:
            message["trace"] = request.context.request_id
            # message["json_fields"]["user"] = request.context.user.id
        self.logger.info('completed handling request', extra=message)
