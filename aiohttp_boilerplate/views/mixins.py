from random import randrange

import ujson as json
from aiocache import cached
from aiohttp import web


def key_builder(f, self, *args, **kwargs):
    _path = ""
    namespace = getattr(self, "namespace", "")
    if namespace:
        namespace += "."

    if f.__name__ == "_options":
        return namespace + self.__class__.__name__

    if self.request.query_string and not self.request.query.get("skip_increment"):
        _path = '?'
        order_key = getattr(self, "order_key", "order")
        for k in sorted(self.request.query.keys()):
            v = self.request.query.get(k)
            if k in order_key and v == "random":
                v += str(randrange(0, 100))

            _path += f"{k}={v}&"

    return namespace + self.request.path + _path


class CacheMixin:
    namespace = ''

    async def skip_page(self):
        pass

    @cached(key_builder=key_builder)
    async def _get(self):
        await self.skip_page()
        data = await super()._get()
        data = json.dumps(data)
        return data

    @cached(key_builder=key_builder)
    async def _options(self):
        data = await super()._options()
        data = json.dumps(data)
        return data

    @staticmethod
    async def increment(data, path):
        pass

    @staticmethod
    def json_response(data, status=200):
        if isinstance(data, dict):
            return super().json_response(data, status)

        return web.json_response(
            text=data,
            status=status,
        )
