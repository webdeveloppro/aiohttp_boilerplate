import json

from aiohttp.test_utils import unittest_run_loop
from aiohttp.test_utils import AioHTTPTestCase
from aiohttp.test_utils import make_mocked_request

from aiohttp_boilerplate.bootstrap import start_web_app
from .load_fixtures import LoadFixture


class BaseTestCase(AioHTTPTestCase):
    url = '/'
    loaded_fixtures = {}
    fixtures = {}

    async def get_application(self):
        """Override the get_app method to return your application.
        """
        # it's important to use the loop passed here.
        app, dbpool, conf = await start_web_app(self.loop)
        self.mocked_request = make_mocked_request(
            'GET',
            '/',
            app=app,
        )

        self.dbpool = dbpool
        self.conf = conf

        return app

    async def request(self, url, method, data={}, headers={}):

        # Do Not share headers and data between tests
        headers_copy = headers.copy()
        data_copy = json.dumps(data)

        headers_copy['content-type'] = headers.get('content-type', 'application/json')
        resp = await self.client.request(method, url, headers=headers_copy, data=data_copy)

        if resp.headers.get('content-type').count('json') > 0:
            jsn = await resp.json()
            return resp.status, jsn or {}
        else:
            return resp.status, await resp.text()

    async def setUpAsync(self):
        if len(self.fixtures.keys()) > 0:
            con = await self.dbpool.acquire()
            for name, path in self.fixtures.items():
                self.loaded_fixtures[name] = await self.load_fixture(path, con)
                print("Loaded: {}: {}".format(path, len(self.loaded_fixtures[name])))

            await self.dbpool.release(con)

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
