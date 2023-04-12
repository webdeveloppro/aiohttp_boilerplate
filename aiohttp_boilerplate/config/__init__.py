import logging
import importlib
import os.path

from ..logging.helpers import NoHeathCheckLogs

# Create as a class
config = {
    'web_run': {
        'host': os.environ.get('HOST'),
        'port': int(os.environ.get('PORT')),
        'access_log_class': NoHeathCheckLogs,
    },
    'postgres': {
        'database': os.environ.get('DB_DATABASE', 'test'),
        'password': os.environ.get('DB_PASSWORD', ''),
        'user': os.environ.get('DB_USER', 'postgres'),
        'host': os.environ.get('DB_HOST', 'localhost'),
        'port': int(os.environ.get('DB_PORT', 5432)),
        'min_size': int(os.environ.get('POSTGRES_MINSIZE', 5)),
        'max_size': int(os.environ.get('POSTGRES_MAXSIZE', 15)),
        'statement_cache_size': int(os.environ.get('STATEMENT_CACHE_SIZE', 0))
    },
    'hostname': os.environ.get('HOSTNAME', ''),
    'AIOCACHE_DISABLE': os.environ.get('AIOCACHE_DISABLE', False),
    'app_dir': os.environ.get('APP_DIR', 'app'),
    'domain': os.environ.get('DOMAIN', 'example.com'),
    'AUTH_URL': os.environ.get('AUTH_URL', ''),
    'DEBUG': int(os.environ.get('DEBUG', 0)),
    'middlewares': [
        'aiohttp_boilerplate.middleware.defaults.cross_origin_rules',
        'aiohttp_boilerplate.middleware.defaults.url_status_200',
        'aiohttp_boilerplate.middleware.defaults.erase_header_server',
    ]
}

# Will merge with app config
try:
    APP = importlib.import_module(f"{config['app_dir']}.config")
    config.update(APP.config)
except ModuleNotFoundError:
    pass


# Incase if you will have to load your config from file or database
async def load_config(loop):
    return config
