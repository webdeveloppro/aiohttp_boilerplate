# Logging module

This module contains custom logging settings for our python apps

We have 2 logger:
- **GCPLogger** (gcp_logger.py) - our default logger, it write logs according to [Google cloud logs structure](https://cloud.google.com/logging/docs/structured-logging)
- **AccessLoggerRequestResponse** (access_log.py) - this loggger override default aiohttp access logger

## Configuration
- LOG_FORMAT
  - json
  - txt
  - colored
- LOG_LEVEL
  - DEBUG
  - INFO
  - WARNING
  - ERROR
- LOG_STACK_INFO
  - true
  - false
- LOG_STACK_LEVEL
  - integer(1-10)

## GCPLogger (gcp_logger.py)
- For use this logger, you can get it from request object:
    ```
      async def get(self):
        self.request.log.error("Error when render document")
    ```
- each log have requered message field and optional error field (or info field for INFO and WARNING logs)
    - message field it's first argument in function call, it should contain only short generic message
    - error or info message it's second argument in function call, it could contain any detailed information
    - example: ```self.request.log.error("Error when render document", "incorrect body: slug filed should be str")```
    - You also can add extra fields to log object using extra argument
    - example: ```self.request.log.error("Error ....", "incorrect ...", extra={"request_id": "id-1"})```
- each log have infomation about request inside serviceContext.httpRequest field
- log json structure (example):
```
{
    "message": "Example log message",
    "component": "aiohttp:server",
    "serviceContext": {
        "httpRequest": {
            "method": "GET",
            "url": "/user/tasks?transaction_id=113&status=all",
            "userAgent": "Mozilla/5.0",
            "referer": "https://dev.yoursunday.pro/",
            "remoteIp": "10.42.1.21",
            "protocol": "http"
        }
    },
    "info": "some details about log",
    "severity": "INFO",
    "level": "info",
    "time": "2024-01-08T03:12:17Z"
}
```

## AccessLoggerRequestResponse (access_log.py)
- this logs have **info** level when response status = 2XX, warning when status = 4xx and error when status = 5xx
- it have response latency and statusCode inside serviceContext.httpRequest field
- log json structure (example):
```
{
    "message": "completed handling request",
    "component": "access-log",
    "level": "info",
    "severity": "INFO",
    "serviceContext": {
        "httpRequest": {
            "method": "GET",
            "url": "/user/emails/partners?transaction_id=113",
            "path": "/user/emails/partners",
            "userAgent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
            "referer": "https://dev.yoursunday.pro/",
            "responseStatusCode": 200,
            "remoteIp": "10.42.1.248",
            "latency": 1.1829999999972642,
            "protocol": "http"
        }
    }
}
```

# ToDo
- [ ] get event loop and add request body in the request.body in access logger
- [ ] get event loop and add response body in the response.body in access logger
- [X] use aiohttp.web as a default logger for the application
