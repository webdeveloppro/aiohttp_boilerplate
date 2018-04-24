import asyncio
import re
import sys

from aiohttp_boilerplate import dbpool as db
from aiohttp_boilerplate.config import CONFIG


class SQLException(Exception):
    pass


# TODO
# Use logging instead of print
class SQL(object):

    def __init__(self, table, conn=None):
        self.conn = conn
        self.table = table
        self.query = ''
        self.params = {}

    def __str__(self):
        return "{} {} {} {}".format(
            self.conn,
            self.table,
            self.query,
            self.params,
        )

    async def get_connection(self):
        if self.conn is None:
            try:
                self.conn = await db.DB_POOL.acquire()
            except:
                loop = asyncio.get_event_loop()
                db.DB_POOL = await db.create_pool(loop=loop)
                self.conn = await db.DB_POOL.acquire()
            # self.conn = await db.create_connection()
            # await db.setup_connection(self.conn)
        return self.conn

    def prepare_where(self, where, params, index=0):
        for i, key in enumerate(params.keys()):
            where = where.replace('{{{}}}'.format(key), '${}'.format(i+index+1))

        missing_params = re.findall(r'{.*}', where)
        if len(missing_params) > 0:
            raise SQLException('Missing parameters {}'.format(','.join(missing_params)))

        return where

    async def release(self):

        if self.conn:
            await db.DB_POOL.release(self.conn)
            self.conn = None

    async def execute(self, query, params, fetch_method='execute'):
        self.query = query
        self.params = params

        await self.get_connection()

        if CONFIG['DEBUG'] > 0:
            print(self.query, self.params.values(), file=sys.stderr)

        try:
            if fetch_method == 'execute':
                result = await self.conn.execute(self.query, *self.params.values())
            elif fetch_method == 'fetch':
                result = await self.conn.fetch(self.query, *self.params.values())
            elif fetch_method == 'fetchrow':
                result = await self.conn.fetchrow(self.query, *self.params.values())
            elif fetch_method == 'fetchval':
                result = await self.conn.fetchval(self.query, *self.params.values())
        finally:
            await self.release()

        return result

    async def select(self, fields='*', where='', order='', limit='', params={}, many=False):

        if self.table is None:
            raise SQLException('table is not set')

        if type(params) != dict:
            raise SQLException('params have to be dict')

        self.params = params
        self.query = 'select {} from {}'.format(fields, self.table)


        if where:
            self.query += ' where {}'.format(self.prepare_where(where, params))

        if order:
            self.query += ' order by {}'.format(order)

        if limit:
            self.query += ' limit {}'.format(limit)

        await self.get_connection()

        if CONFIG['DEBUG'] > 0:
            print(self.query, self.params.values(), file=sys.stderr)

        if CONFIG.get('TRACEBACK', 0) > 0:
            import traceback
            print('\n'.join([str(line) for line in traceback.extract_stack()]), file=sys.stderr)

        try:
            if many:
                result = await self.conn.fetch(self.query, *self.params.values())
            else:
                result = await self.conn.fetchrow(self.query, *self.params.values())
        finally:
            await self.release()

        return result

    async def insert(self, params={}):
        sql = params.pop('sql', '')
        self.query = 'insert into {}({}) values({}) {} RETURNING id'.format(
            self.table,
            ','.join(params.keys()),
            ','.join(['$%d' % (x+1) for x in range(0, params.__len__())]),
            sql
        )
        # self.params = self._prepare_fields(params)

        await self.get_connection()

        if CONFIG['DEBUG'] > 0:
            print(self.query, *params.values(), file=sys.stderr)

        try:
            result = await self.conn.fetchval(self.query, *params.values())
        finally:
            await self.release()

        return result

    async def update(self, where='', params={}, data={}):
        self.query = 'update {}'.format(self.table)

        if data:
            self.query += ' set '
            self.query += ','.join([key + '=$%d' % (i+1) for i, key in enumerate(data.keys())])
        if where:
            self.query += ' where {}'.format(self.prepare_where(where, params, len(data)))

        self.params = data
        self.params.update(params)
        # self.params = self._prepare_fields(self.params)

        await self.get_connection()

        if CONFIG['DEBUG'] > 0:
            print(self.query, self.params.values(), file=sys.stderr)

        try:
            result = await self.conn.execute(self.query, *self.params.values())
        finally:
            await self.release()

        return int(result.replace('UPDATE ', ''))

    async def delete(self, where='', params={}):
        self.query = 'delete from {}'.format(self.table)

        if where:
            self.query += ' where {}'.format(self.prepare_where(where, params))

        self.params = params

        await self.get_connection()

        if CONFIG['DEBUG'] > 0:
            print(self.query, self.params.values(), file=sys.stderr)

        try:
            result = await self.conn.execute(self.query, *params.values())
        finally:
            await self.release()

        return int(result.replace('DELETE ', ''))

    async def get_count(self, where='', params={}):
        self.query = 'select count(*) as count from {}'.format(self.table)

        if where:
            self.query += ' where {}'.format(self.prepare_where(where, params))

        self.params = params

        await self.get_connection()

        if CONFIG['DEBUG'] > 0:
            print(self.query, self.params.values(), file=sys.stderr)

        try:
            result = await self.conn.fetchval(self.query, *params.values())
        finally:
            await self.release()

        return result

    async def is_exists(self, where, params):

        # print('before connection ', self, where, params, 'q=', self.query, self.params)
        await self.get_connection()

        # print('after connection ', self, where, params, 'q=', self.query, self.params)
        query = "SELECT 1 as t FROM {} WHERE {}".format(
            self.table,
            self.prepare_where(where, params)
        )

        self.query = query
        self.params = params

        if CONFIG['DEBUG'] > 0:
            print(self.query, self.params.values(), file=sys.stderr)

        try:
            result = await self.conn.fetchval(self.query, *self.params.values())

            if result is None:
                result = False
            else:
                result = True

        finally:
            await self.release()

        return result
