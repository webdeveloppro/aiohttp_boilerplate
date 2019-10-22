import asyncio
import logging
from pathlib import Path

import uvloop
from aiohttp import web
from asyncpg.exceptions import PostgresError

from aiohttp_boilerplate import config
from aiohttp_boilerplate.dbpool import pg as db
from .console_app import start_console_app
from .web_app import start_web_app

__all__ = ('web_app', 'console_app', 'get_loop',)


def get_loop():
    # TODO
    # Test logging
    logging.basicConfig(
        level=logging.DEBUG if config.config.get('DEBUG') else logging.INFO
    )
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()
    return loop


async def migration_sql(dbpool, conf):
    if conf.get('DEBUG', False):
        logger = logging.getLogger('sql.migration')

        file = Path('sql/migrations.sql')

        if file.exists():
            with file.open() as f:
                logger.info("Read file sql/migrations.sql")
                sql_query = f.read()
                if sql_query:
                    async with dbpool.acquire() as conn:
                        async with conn.transaction():
                            logger.info("Making migration...")
                            try:
                                await conn.execute(sql_query)
                            except PostgresError as e:
                                logger.error(f"Migration failed {e}")


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
    web.run_app(app, **conf['web_run'])
