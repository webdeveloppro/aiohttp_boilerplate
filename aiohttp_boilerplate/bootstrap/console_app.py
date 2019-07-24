class ConsoleApp:
    conf = {}
    db_pool = None
    loop = None


def start_console_app(conf, db_pool, loop=None):
    # setup application and extensions
    app = ConsoleApp()
    app.conf = conf
    app.db_pool = db_pool
    app.loop = loop
    return app
