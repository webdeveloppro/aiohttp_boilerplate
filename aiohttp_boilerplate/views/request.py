from aiohttp import web
from logging import Logger

# ToDo
# Add REPOSITORY, GIT_COMMIT, BUILD_DATE, SERVICE_NAME to the logging
class ServiceContext(object):
    service: str
    version: str

class Context(object):
    request_id: str
    user: str
    version: str
    service_name: str
    service_context: ServiceContext
