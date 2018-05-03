class FakeConnection(object):

    def __init__(self):
        class test:
            pass

        self._protocol = test()
        self._protocol.queries_count = 0

    async def set_type_codec(*args, **kwargs):
        pass

    def is_closed(self):
        return False

    async def fetchrow(self, query, *params):
        return False

    async def reset(self):
        return False


class FakeDBPool(object):

    _max_queries = 100

    async def acquire(self):
        return FakeConnection()

    async def release(self, conn):
        pass
