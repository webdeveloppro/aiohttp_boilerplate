import asyncio

try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ModuleNotFoundError:
    pass

from aiohttp import web
from aiohttp_boilerplate import config
from aiohttp_boilerplate.dbpool import pg as db
from aiohttp_boilerplate import logging as blogging
from aiohttp_boilerplate.logging import access_log, gcp_logger

from .console_app import start_console_app
from .web_app import start_web_app

__all__ = ('web_app', 'console_app', 'get_loop',)


def get_loop() -> asyncio.AbstractEventLoop:
    try:
        return asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop

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

    blogging.setup_global_logger(conf['log']['format'], conf['log']['level'])

    db_pool = loop.run_until_complete(db.create_pool(
        conf=conf['postgres'],
        loop=loop,
    ))

    app = start_web_app(conf, db_pool, loop)
    log = gcp_logger.GCPLogger("web_app")
    runner = web.AppRunner(app, logger=log, access_log_class=access_log.AccessLoggerRequestResponse)
    loop.run_until_complete(runner.setup())
    site = web.TCPSite(runner, host=conf['web_run']['host'], port=conf['web_run']['port'])
    loop.run_until_complete(site.start())
    log.info(f"starting server on {conf['web_run']['host']}:{conf['web_run']['port']}")
    loop.run_forever()
