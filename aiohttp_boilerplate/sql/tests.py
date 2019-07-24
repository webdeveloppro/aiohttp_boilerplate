import asyncio
from unittest import mock

from aiohttp_boilerplate import dbpool as db
from aiohttp_boilerplate import sql


class MyConnection(object):

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


class MyDBPOOL(object):

    _max_queries = 100

    async def acquire(self):
        return MyConnection()

    async def release(self, conn):
        print('released')


def getSQL(loop):
    db.DB_POOL = MyDBPOOL()
    return sql.SQL('table')


@asyncio.coroutine
async def tttest_get_connection(loop):
    """
        Make sure that acquire was called
    """
    # ToDo
    # I Feel like we need to use mock object here

    db.DB_POOL = MyDBPOOL()
    sqlObject = sql.SQL('table')
    conn = await sqlObject.get_connection()
    assert isinstance(conn, MyConnection)

    # Test that acquire was called only once
    sqlObject.conn.test = 1
    conn = await sqlObject.get_connection()
    assert sqlObject.conn.test == 1


def test_prepare_where(loop):
    """
        Make sure we building right sql query
    """
    sqlObject = sql.SQL('table')

    # Test where
    where = "id={id} and owner_id={owner_id} and user_id in ({owner_id})"
    params = {
        'id': 5,
        'owner_id': 26
    }

    assert "id=$1 and owner_id=$2 and user_id in ($2)" == sqlObject.prepare_where(
            where,
            params
        )

    # Test index
    assert "id=$6 and owner_id=$7 and user_id in ($7)" == sqlObject.prepare_where(
            where,
            params,
            5
        )

    # ToDO
    # Add tests for set_codecs !!


@asyncio.coroutine
async def test_release(loop):
    pass


@asyncio.coroutine
async def test_execute(loop):
    pass


@asyncio.coroutine
async def test_select(loop):
    """
        Test different SQL select queries
    """

    fields = "t0.id, t1.phone"
    where = "id={id} and owner_id={owner_id} or t2.user_id = {owner_id}"
    params = {
        'id': 12,
        'owner_id': 45
    }
    order = 'id desc'
    limit = '100 offset 5'

    with mock.patch('asyncpg.pool.Pool._new_connection') as mockConnection:

        async def new_connection(self):
            return MyConnection()

        mockConnection.return_value = new_connection(None)

        db.DB_POOL = await db.create_pool()

        async def new_fetchrow(self, query, *params):
            assert query == "select t0.id, t1.phone from table_name "
            "where id=$1 and owner_id=$2 or t2.user_id=$2"
            "order by id desc "
            "limit 100 offset 5",
            assert params == [12, 45]
            print(f"called with {query} {params}")

        sqlObject = sql.SQL('table_name')
        sqlObject.fetchrow = new_fetchrow
        await sqlObject.select(
            fields,
            where,
            order,
            limit,
            params
        )


@asyncio.coroutine
async def test_prepare_where_missed_param(loop):
    """
        Test different SQL select queries
    """

    fields = "t0.id, t1.phone"
    where = "id={_id} and owner_id={owner_id} or t2.user_id = {owner_id}"
    params = {
        'id': 12,
        'owner_id': 45
    }
    order = 'id desc'
    limit = '100 offset 5'

    with mock.patch('asyncpg.pool.Pool._new_connection') as mockConnection:

        async def new_connection(self):
            return MyConnection()

        mockConnection.return_value = new_connection(None)

        db.DB_POOL = await db.create_pool()

        try:
            sqlObject = sql.SQL('table_name')
            await sqlObject.select(
                fields,
                where,
                order,
                limit,
                params
            )
            assert 'Select should throw exception' == 'but not throwed'
        except sql.SQLException as e:
            assert str(e) == 'Missing parameters {_id}'


@asyncio.coroutine
async def test_insert(loop):
    pass


@asyncio.coroutine
async def test_update(loop):
    """
        Test different SQL select queries
    """

    where = "id={id} and owner_id={owner_id} or t2.user_id={owner_id}"
    params = {
        'id': 12,
        'owner_id': 45
    }
    new_data = {
        'password': 'new_password',
        'api_key': 'new_api_key'
    }

    with mock.patch('asyncpg.pool.Pool._new_connection') as mockConnection:

        async def new_execute(self, query, *params):
            print(f"called with {query} {params}")
            assert query == "update table_name "\
                "set password=$1,api_key=$2 "\
                "where id=$3 and owner_id=$4 or t2.user_id=$4"
            assert params == ('new_password', 'new_api_key', 12, 45)
            return 'UPDATE 1'

        MyConnection.execute = new_execute

        async def new_connection(self):
            return MyConnection()

        mockConnection.return_value = new_connection(None)

        db.DB_POOL = await db.create_pool()

        sqlObject = sql.SQL('table_name')
        await sqlObject.update(
            where,
            params,
            new_data
        )


@asyncio.coroutine
async def test_delete(loop):
    pass


@asyncio.coroutine
async def test_get_count(loop):
    pass
