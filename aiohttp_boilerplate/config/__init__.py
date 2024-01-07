import environ
import importlib

# reading .env file
environ.Env.read_env()
env = environ.Env() # FixMe, read .env from application home dir

conf = None

# TODO: Find lib for partial initialization of the config
def get_config(name=None):
    global conf

    if conf is None:
        conf = {
            'web_run': {
                'host': env.str('HOST'),
                'port': env.int('PORT'),
                'access_log_class': None,
            },
            'log': {
                'level': env.str('LOG_LEVEL'),
                'format': env.str('LOG_FORMAT'),
                'stackinfo': env.bool('LOG_STACK_INFO', False),
                'stacklevel': env.int('LOG_STACK_LEVEL', 3),
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

    if name is None:
        return conf
    elif name not in conf:
        raise ModuleNotFoundError

    return conf[name]

# Incase if you will have to load your config from file or database
async def load_config():
    # Create as a class
    config = get_config()

    # Will merge with app config
    try:
        app_dir_config = importlib.import_module(f"{config['app_dir']}.config")
        config.update(app_dir_config.config)
    except ModuleNotFoundError:
        pass
    
    return config
