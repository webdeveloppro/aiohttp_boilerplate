import environ
import importlib

from ..logging.helpers import GCPLogger

# reading .env file
environ.Env.read_env()
env = environ.Env() # FixMe, read .env from application home dir


# Create as a class
config = {
    'web_run': {
        'host': env.str('HOST'),
        'port': env.int('PORT'),
        'access_log_class': None,
    },
    'postgres': {
        'database': env.str('DB_DATABASE'),
        'password': env.str('DB_PASSWORD'),
        'user': env.str('DB_USER'),
        'host': env.str('DB_HOST'),
        'port': env.int('DB_PORT'),
        'min_size': env.int('DB_MIN_CONNECTIONS', 2),
        'max_size': env.int('DB_MAX_CONNECTIONS'),
        'statement_cache_size': env.int('DB_STATEMENT_CACHE_SIZE', 0),
        'max_inactive_connection_lifetime': env.int('DB_MAX_INACTIVE_CONNECTION_LIFETIME', 300)
        # ToDo
        # Add hostname to the db
        # ToDo
        # Add DB_SSL_MODE parameter
    },
    'hostname': env.str('HOSTNAME', ''),
    'AIOCACHE_DISABLE': env.bool('AIOCACHE_DISABLE', False),
    'app_dir': env.str('APP_DIR', 'app'),
    'domain': env.str('DOMAIN'),
    'AUTH_URL': env.str('AUTH_URL', ''), # ToDo move to auth service
    'middlewares': [
        'aiohttp_boilerplate.middleware.defaults.cross_origin_rules',
        'aiohttp_boilerplate.middleware.defaults.url_status_200',
        'aiohttp_boilerplate.middleware.defaults.erase_header_server',
        'aiohttp_boilerplate.middleware.logger_to_request.logger_to_request',
        'aiohttp_boilerplate.middleware.x_request_id.x_request_id',
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
