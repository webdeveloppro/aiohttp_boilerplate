import asyncio
import logging
import uvloop

from aiohttp import web

from aiohttp_boilerplate import config
from aiohttp_boilerplate.dbpool import pg as db
from .console_app import start_console_app
from .web_app import start_web_app

__all__ = ('web_app', 'console_app', 'get_loop', )


def get_loop():
    # TODO
    # Test logging
    logging.basicConfig()
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()
    return loop


def console_app():
    loop = get_loop()
    conf = loop.run_until_complete(config.load_config(loop=loop))
    db_pool = loop.run_until_complete(db.create_pool(
        loop=loop,
        conf=conf['postgres']
    ))
    console_app = start_console_app(conf, db_pool, loop)
    return console_app


def web_app():
    loop = get_loop()
    conf = loop.run_until_complete(config.load_config(loop=loop))
    db_pool = loop.run_until_complete(db.create_pool(
        conf=conf['postgres'],
        loop=loop,
    ))
    web_app = start_web_app(conf, db_pool, loop)
    web.run_app(web_app, host=conf['host'], port=conf['port'])
