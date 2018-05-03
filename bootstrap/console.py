class ConsoleApp:
    conf = {}
    db_pool = None


def start_console_app(conf=None, db_pool=None, loop=None):
    # load config from yaml file in current dir

    if loop is None:
        loop = get_loop()

    if config is None:
        config = loop.run_until_complete(load_config())

    if db_pool is None:
        db_pool = loop.run_until_complete(db_pool.create_pool(config=conf, loop=loop))

    # setup application and extensions
    app = ConsoleApp()
    app.conf = config
    app.db_pool = db_pool
    return loop
