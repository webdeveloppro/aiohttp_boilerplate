import logging
from aiohttp.abc import AbstractAccessLogger

def skipHealtcheck(record) -> bool:
    return record.http_request["headers"]["path"] == "/healtcheck"

class AccessLoggerRequestResponse(AbstractAccessLogger):
    exception = dict

    def __init__(self, logger: logging.Logger, log_format: str) -> None:
        super().__init__(logger, log_format=log_format)
        self.logger.addFilter(skipHealtcheck)

    def log(self, request, response, time):
        headers = {}
        for key, val in request.headers.items():
            headers[key.lower()] = val
        headers['method'] = request.method
        headers['path'] = request.path
        headers['query'] = dict(request.query)
        headers['scheme'] = request.scheme
        
        print('for each headers', headers)
        message = {
            "http_request": {
                "headers": headers,
                # FixMe: get event loop and read body
                # body: await request.text()
                "body": "", 
            },
            "http_response": {
                "headers": response.headers,
                "size": response.content_length,
                "status": response.status,
                "text_status": "", # FixMe: get event loop and read body
                "took": time,
            }
        }
        self.logger.debug('completed handling request', extra=message)