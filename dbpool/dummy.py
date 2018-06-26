from aiohttp_boilerplate import dbpool


class Connection(object):

    def __init__(self):
        # ToDo
        # Use some readstream from aiohttp.streams
        class test:
            pass

        self._protocol = test()
        self._protocol.queries_count = 0
        self.return_data = None

    async def set_type_codec(*args, **kwargs):
        pass

    def is_closed(self):
        return False

    async def fetchrow(self, query, *params):
        return self.return_data

    async def fetchval(self, query, *params):
        return self.return_data

    async def reset(self):
        return self.return_data


class DBPool(object):

    _max_queries = 100

    async def acquire(self):
        return Connection()

    async def release(self, conn):
        pass

    async def close(self):
        pass


async def create_pool(conf, loop=None):

    dbpool.DB_POOL = DBPool()
    return dbpool.DB_POOL
