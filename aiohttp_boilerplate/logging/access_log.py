import logging
from aiohttp.abc import AbstractAccessLogger

def skipHealtcheck(record) -> bool:
    return record.serviceContext["httpRequest"]["path"] == "/healtcheckd"

class AccessLoggerRequestResponse(AbstractAccessLogger):
    def __init__(self, logger: logging.Logger, log_format: str) -> None:
        super().__init__(logger, log_format=log_format)
        # self.logger.addFilter(skipHealtcheck)

    def log(self, request, response, time):
        message = {
            "component": "access-log",
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
            },
            "json_fields": {}
        }
        if "context" in request:
            message["trace"] = request.context.request_id
            # message["json_fields"]["user"] = request.context.user.id
        self.logger.debug('completed handling request', extra=message)
