import asyncio
import uvloop

from aiohttp import web
from aiohttp_boilerplate import config
from aiohttp_boilerplate.dbpool import pg as db


from .console_app import start_console_app
from .web_app import start_web_app

__all__ = ('web_app', 'console_app', 'get_loop',)


def get_loop() -> asyncio.AbstractEventLoop:

    # ToDo
    # Check if asyncio does not have any event loop already?
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    return asyncio.get_event_loop()

def console_app(loop=None):
    if loop is None:
        loop = get_loop()

    conf = loop.run_until_complete(config.load_config(loop=loop))
    db_pool = loop.run_until_complete(db.create_pool(
        loop=loop,
        conf=conf['postgres']
    ))
    return start_console_app(conf, db_pool, loop)


def web_app():
    loop = get_loop()
    conf = loop.run_until_complete(config.load_config(loop=loop))
    db_pool = loop.run_until_complete(db.create_pool(
        conf=conf['postgres'],
        loop=loop,
    ))

    app = start_web_app(conf, db_pool, loop)
    web.run_app(app=app, loop=loop, **conf['web_run'])
