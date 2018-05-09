class ConsoleApp:
    conf = {}
    db_pool = None


def start_console_app(conf, db_pool, loop=None):
    # setup application and extensions
    app = ConsoleApp()
    app.conf = conf
    app.db_pool = db_pool
    return app
