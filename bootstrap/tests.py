import asyncio
from unittest import mock

from aiohttp_boilerplate import bootstrap
from aiohttp_boilerplate import config
from aiohttp_boilerplate.dbpool import tests as db_tests


@asyncio.coroutine
async def test_start_web_app(loop):
    """
        Should:
            - run web.Application with custom middlewares
            - import app routers
            - call close on delete
    """

    config.CONFIG['middlewares'] = [
        'aiohttp_boilerplate.middleware.defaults.cross_origin_rules',
    ]
    config.CONFIG['app_dir'] = 'tests'
    db_pool = db_tests.FakeDBPool()

    app = bootstrap.start_web_app(config.CONFIG, db_pool, loop)
    assert callable(app.middlewares[0])
    assert callable(app.on_cleanup[0])
    assert callable(app.on_shutdown[0])
