import logging
import os
from logging import config as log_config

from pkg_resources import resource_filename

from .formatter import JsonFormatter


def _resolve(name):
    import importlib
    """Resolve a dotted name to a global object."""
    name = name.split('.')
    used = name.pop(0)
    found = importlib.import_module(used)
    for n in name:
        used = used + '.' + n
        try:
            found = getattr(found, n)
        except AttributeError:
            found = importlib.import_module(used)
    return found


log_config._resolve = _resolve

LOG_LEVEL = logging.DEBUG if os.environ.get("DEBUG", "false").lower() in ['true', '1'] else logging.INFO

try:
    file = os.environ.get('LOG_CONFIG', resource_filename(__name__, 'logger.conf'))
    log_config.fileConfig(file)
except Exception:
    print('Couldn\'t load default configuration data. Something went wrong with the '
          'installation.')
    import traceback
    import sys

    exc_info = sys.exc_info()
    traceback.print_exception(*exc_info)
    del exc_info
    sys.exit(1)


def get_logger(name=None):
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)
    return logger


sql_logger = get_logger('aiohttp_boilerplate.sql')
view_logger = get_logger('aiohttp_boilerplate.views')
