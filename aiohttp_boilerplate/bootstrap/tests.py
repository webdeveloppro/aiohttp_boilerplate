import asyncio

from aiohttp_boilerplate import bootstrap
from aiohttp_boilerplate import config
from aiohttp_boilerplate.dbpool import dummy


@asyncio.coroutine
async def test_start_web_app(loop):
    """
        Check:
        - run web.Application with custom middlewares
        - import app routers
        - call close on delete
    """

    config.config['middlewares'] = [
        'aiohttp_boilerplate.middleware.defaults.cross_origin_rules',
    ]
    config.config['app_dir'] = 'tests'
    db_pool = dummy.DBPool()

    app = bootstrap.start_web_app(config.config, db_pool, loop)
    assert callable(app.middlewares[0])
    assert callable(app.on_cleanup[0])
    assert callable(app.on_shutdown[0])


@asyncio.coroutine
async def test_start_console_app(loop):
    """
        Check:
        - config is generated
        - dbpool is created
    """

    DBPool = dummy.DBPool()
    app = bootstrap.console.start_console_app(
        conf=config.config,
        db_pool=DBPool,
    )

    assert app.conf == config.config
    assert app.db_pool == DBPool
