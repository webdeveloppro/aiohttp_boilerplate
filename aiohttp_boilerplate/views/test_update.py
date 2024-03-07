import unittest
import logging
import pytest

from aiohttp import web
from .update import UpdateView


def get_schema(self):
    return {}

UpdateView.get_schema = get_schema


class TestUpdate(unittest.IsolatedAsyncioTestCase):
    def create_request(self):
        class FakeRequest:
            log: logging.Logger
            app: object
        class FakeApp:
            db_pool = None
        request = FakeRequest()
        request.log = logging.getLogger('aiohttp:test')
        request.app = FakeApp()
        setattr(request.app, 'db_pool', None)
        return request

    async def test_validate_empty_body(self):
        up = UpdateView(self.create_request())
        up.get_schema = lambda: {}
        with pytest.raises(web.HTTPBadRequest) as excinfo:
            await up._patch({})
        assert str(excinfo.value) == "Bad Request"
