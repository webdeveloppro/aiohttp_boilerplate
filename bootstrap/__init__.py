import asyncio
import logging
import uvloop
import importlib

from aiohttp import web

from aiohttp_boilerplate import config
from aiohttp_boilerplate import dbpool


async def on_cleanup(app):
    # await app.db_pool.release(app.db)
    # await app.db_pool.terminate()
    await app.db_pool.close()


def get_loop():
    # TODO
    # Test logging
    logging.basicConfig()
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()
    return loop


def start_web_app(conf, db_pool, loop=None):

    middlewares = []

    if conf.get('middlewares'):
        for middleware in conf['middlewares']:
            p, m = middleware.rsplit('.', 1)
            mod = importlib.import_module(p)
            met = getattr(mod, m)
            middlewares.append(met)

    # setup application and extensions
    app = web.Application(loop=loop, middlewares=middlewares)
    app.conf = conf
    app.db_pool = db_pool

    app.on_cleanup.append(on_cleanup)
    app.on_shutdown.append(on_cleanup)

    routes = importlib.import_module(conf['app_dir'] + '.routes')
    routes.setup_routes(app)
    return app


def main():
    loop = get_loop()
    conf = loop.run_until_complete(config.load_config(loop=loop))
    print("conf ", conf)
    db_pool = loop.run_until_complete(dbpool.create_pool(loop=loop, conf=conf))
    web_app = start_web_app(conf, db_pool, loop)
    web.run_app(web_app, host=conf['host'], port=conf['port'])


if __name__ == '__main__':
    main()
