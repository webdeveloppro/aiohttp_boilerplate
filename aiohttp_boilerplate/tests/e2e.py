from .unit import UnitTestCase
from .load_fixtures import LoadFixture

from aiohttp_boilerplate import config
from aiohttp_boilerplate.bootstrap import start_web_app
from aiohttp_boilerplate.dbpool import pg as db


class E2ETestCase(UnitTestCase):
    '''
        E2E make real database connection
        Auto fixtures loading
    '''
    loaded_fixtures = {}
    fixtures = {}

    async def get_application(self):
        """Override the get_app method to return your application.
        """
        # it's important to use the loop passed here.
        conf = await config.load_config()
        db_pool = await db.create_pool(
            conf=conf['postgres'],
            loop=self.loop,
        )

        app = start_web_app(
            conf=conf,
            db_pool=db_pool,
            loop=self.loop,
        )

        app.db_pool = db_pool
        self.conf = conf
        return app

    async def setUpAsync(self):
        if len(self.fixtures.keys()) > 0:
            con = await self.app.db_pool.acquire()
            for name, path in self.fixtures.items():
                self.loaded_fixtures[name] = await self.load_fixture(path, con)
                print("Loaded: {}: {}".format(path, len(self.loaded_fixtures[name])))

            await self.app.db_pool.release(con)

    async def load_fixture(self, path, con):

        directory, _file = path.rsplit('/', 1)
        fixture = LoadFixture(_file, directory)

        try:
            async with con.transaction():
                print('Loading {}'.format(path))
                await fixture.file2db(con)
        except Exception as e:
            raise Exception("cannot upload file {}, {}".format(path, str(e)))

        return fixture.data
