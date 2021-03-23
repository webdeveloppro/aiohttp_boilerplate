import asyncio
import logging
import sys
import uvloop

from aiohttp import web
from asyncpg.exceptions import PostgresError
from aiohttp_boilerplate import config
from aiohttp_boilerplate.dbpool import pg as db
from pathlib import Path

from .console_app import start_console_app
from .web_app import start_web_app

__all__ = ('web_app', 'console_app', 'get_loop',)


def get_loop():

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()
    return loop


async def migration_sql(db_pool, conf, path_to_file):
    logger = logging.getLogger('sql.migration')

    file = Path(path_to_file)

    if file.exists():
        with file.open() as f:
            logger.debug('Read file {}'.format(path_to_file))
            sql_query = f.read()
            if sql_query:
                async with db_pool.acquire() as conn:
                    async with conn.transaction():
                        logger.info("Making migration...")
                        try:
                            await conn.execute(sql_query)
                            logger.info('Successfully applied migration from sql/migrations.sql')
                        except PostgresError as e:
                            logger.error(f"Migration failed {e}")
    else:
        logger.error('file {} does not exist'.format(path_to_file))

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

    if 'migrate' in sys.argv:
        file_to_path = sys.argv.pop()
        loop.run_until_complete(migration_sql(db_pool, conf, file_to_path))
        return

    app = start_web_app(conf, db_pool, loop)
    web.run_app(app, **conf['web_run'])
