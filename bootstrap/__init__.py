import asyncio
import logging
import os
import sys
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
    logging.basicConfig()
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()
    return loop


async def migration_sql(dbpool, conf):
    if conf.get('DEBUG', False):
        logger = logging.getLogger('sql.migration')
        base_dir = conf.get(
            'BASE_DIR',
            os.path.dirname(os.path.dirname(sys.modules['__main__'].__file__))
        )
        file = base_dir / Path('sql/migrations.sql')

        if file.exists():
            with file.open() as f:
                logger.info("Read file sql/migration.sql")
                sql_query = f.read()
                if sql_query:
                    async with dbpool.acquire() as conn:
                        async with conn.transaction():
                            logger.info("Making migration...")
                            try:
                                await conn.execute(sql_query)
                            except PostgresError as e:
                                logger.error(f"Migration failed {e}")


def console_app():
    loop = get_loop()
    conf = loop.run_until_complete(config.load_config(loop=loop))
    db_pool = loop.run_until_complete(db.create_pool(
        loop=loop,
        conf=conf['postgres']
    ))
    loop.run_until_complete(migration_sql(db_pool, conf))
    console_app = start_console_app(conf, db_pool, loop)
    return console_app


def web_app():
    loop = get_loop()
    conf = loop.run_until_complete(config.load_config(loop=loop))
    db_pool = loop.run_until_complete(db.create_pool(
        conf=conf['postgres'],
        loop=loop,
    ))
    loop.run_until_complete(migration_sql(db_pool, conf))
    web_app = start_web_app(conf, db_pool, loop)
    web.run_app(web_app, host=conf['host'], port=conf['port'])
