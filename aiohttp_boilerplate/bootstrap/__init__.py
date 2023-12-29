import asyncio

try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ModuleNotFoundError:
    pass

import logging
from pythonjsonlogger import jsonlogger

from aiohttp import web
from aiohttp_boilerplate import config
from aiohttp_boilerplate.dbpool import pg as db
from aiohttp_boilerplate.logging import access_log, gcp_logger


from .console_app import start_console_app
from .web_app import start_web_app

__all__ = ('web_app', 'console_app', 'get_loop',)


def get_loop() -> asyncio.AbstractEventLoop:
    return asyncio.get_event_loop()

def console_app(loop=None):
    if loop is None:
        loop = get_loop()

    conf = loop.run_until_complete(config.load_config())
    db_pool = loop.run_until_complete(db.create_pool(
        loop=loop,
        conf=conf['postgres']
    ))
    return start_console_app(conf, db_pool, loop)


def web_app():
    loop = get_loop()
    conf = loop.run_until_complete(config.load_config())

    setup_global_logger(conf['log']['format'], conf['log']['level'])

    db_pool = loop.run_until_complete(db.create_pool(
        conf=conf['postgres'],
        loop=loop,
    ))

    app = start_web_app(conf, db_pool, loop)
    runner = web.AppRunner(app, access_log_class=access_log.AccessLoggerRequestResponse)
    # runner._kwargs["_cls"] = Request
    loop.run_until_complete(runner.setup())
    site = web.TCPSite(runner, host=conf['web_run']['host'], port=conf['web_run']['port'])
    loop.run_until_complete(site.start())
    loop.run_forever()

def setup_global_logger(format, level):
    logging.setLoggerClass(gcp_logger.GCPLogger)
    logger = logging.getLogger()
    logHandler = logging.StreamHandler()
    logger.handlers = []

    if format == 'json':
        formatter = jsonlogger.JsonFormatter()
        logHandler.setFormatter(formatter)

    logger.addHandler(logHandler)
    logger.setLevel(level.upper())