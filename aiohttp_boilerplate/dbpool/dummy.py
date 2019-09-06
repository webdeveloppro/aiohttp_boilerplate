from aiohttp_boilerplate import dbpool


class Transaction:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


class Connection(object):

    def __init__(self):
        # ToDo
        # Use some readstream from aiohttp.streams
        class test:
            pass

        self._protocol = test()
        self._protocol.queries_count = 0
        self.return_data = None

    async def return_data(self, *args, **kwargs):
        return None

    execute = fetch = fetchval = fetchrow = reset = return_data

    async def set_type_codec(*args, **kwargs):
        pass

    async def prepare(self, *args, **kwargs):
        return self

    def is_closed(self):
        return False

    async def add_listener(self, channel, callback):
        return self.return_data

    def transaction(self):
        return Transaction()


class DBPool(object):
    _max_queries = 100

    async def acquire(self):
        return Connection()

    async def release(self, conn):
        pass

    async def close(self):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


async def create_pool(conf, loop=None):
    dbpool.DB_POOL = DBPool()
    return dbpool.DB_POOL
