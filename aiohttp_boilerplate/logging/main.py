import json
import logging

import google.cloud.logging
from aiohttp_boilerplate.logging.helpers import GCPLogger

client = google.cloud.logging.Client()


def main():
    # Alternatively, but not recommended. It's helpful when you can't set an environment variable.
    service_key_path = "/Users/vladsmac/projects/smplytitle/user-api/aiohttp_boilerplate/logging/logging-gcp.json"
    client = google.cloud.logging.Client.from_service_account_json(service_key_path)
    client.setup_logging()
    # handler = CloudLoggingHandler(client)

    logging.setLoggerClass(GCPLogger)
    log = logging.getLogger("db-pool")
    log.setLevel(logging.INFO)
    log.setComponent("db-pool")
    
    """
    data_dict2 = {
        # "type_": "type.googleapis.com/google.devtools.clouderrorreporting.v1beta1.ReportedErrorEvent",
        "json_fields": {
          "@type": "type.googleapis.com/google.devtools.clouderrorreporting.v1beta1.ReportedErrorEvent",
          "component": "dbpool",
          "error": "Development error description",
          "user": "user 123-123-123",
          "serviceContext": {
            "service": "user-api",
            "version": "unknown:1aea9c2",
          },
        },
        "http_request": {
            "requestMethod": "POST",
            "requestUrl": "/asdg?a=10",
            "userAgent": "mozilla",
            "referer": "",
            # "status": "",
            "remoteIp": "10.10.0.1",
            # "latency": "",
            "protocol": "http",
        },
        "trace": "123-123-123",
    }
    """
    log.error("My Error Message ") # , "developer message")

if __name__ == "__main__":
    main()
