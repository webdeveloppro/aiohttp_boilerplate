import os
import logging
from aiohttp import web
from ..views import Context

# Create logger in request with all info
@web.middleware
async def logger_to_request(request:web.Request, handler):
    if "context" not in request:
        request.context = Context

    service_name = os.getenv("SERVICE_NAME")
    log = logging.getLogger(service_name or "aiohttp:server")

    git_commit = os.getenv("GIT_COMMIT")
    build_date = os.getenv("BUILD_DATE")
    repository = os.getenv("REPOSITORY")

    if service_name:
        request.context.service_name = service_name
    if git_commit or build_date:
        request.context.version = f'{git_commit}:{build_date}'
    if repository:
        request.context.sourceReference = {
            "repository":f"{repository}",
            "revisionId":f"{git_commit}",
        }

    log.setRequest(request)
    request.log = log
    response = await handler(request)
    log.setResponse(response)
    return response