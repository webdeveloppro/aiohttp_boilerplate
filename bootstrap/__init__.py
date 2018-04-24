import asyncio
import logging
import uvloop
import importlib

from aiohttp import web

from aiohttp_boilerplate.config import load_config
from aiohttp_boilerplate import dbpool as db


async def on_cleanup(app):
    # await app.db_pool.release(app.db)
    # await app.db_pool.terminate()
    await app.db_pool.close()


def start_console_app(loop=None):
    # load config from yaml file in current dir

    if loop is None:
        loop = get_loop()

    class FakeApp:
        conf = {}

    # setup application and extensions
    app = FakeApp()
    app.conf = loop.run_until_complete(load_config())

    # Creates DB POOL connection
    db_pool = loop.run_until_complete(db.create_pool(loop=loop))
    db.DB_POOL = db_pool
    app.DB_POOL = db_pool

    return loop, app, db_pool


async def start_web_app(loop):

    middlewares = []
    conf = await load_config()

    if conf.get('middlewares'):
        for middleware in conf['middlewares']:
            p, m = middleware.rsplit('.', 1)
            mod = importlib.import_module(p)
            met = getattr(mod, m)
            middlewares.append(met)

    # setup application and extensions
    app = web.Application(loop=loop, middlewares=middlewares)
    app.conf = conf

    # !!! WILL CREATE DATABASE POOL !!!
    app.db_pool = await db.create_pool(loop=loop)
    db.DB_POOL = app.db_pool

    app.on_cleanup.append(on_cleanup)

    from app.routes import setup_routes
    setup_routes(app)

    return app, db.DB_POOL, app.conf


def get_loop():
    # TODO
    # Test logging
    logging.basicConfig()
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()
    return loop


def main():
    loop = get_loop()
    app, db_pool, config = loop.run_until_complete(start_web_app(loop))
    web.run_app(app, host=config['host'], port=config['port'])


if __name__ == '__main__':
    main()
