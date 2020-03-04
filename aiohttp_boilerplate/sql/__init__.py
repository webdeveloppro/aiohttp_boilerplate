import asyncio
import re

from aiohttp_boilerplate import dbpool
from aiohttp_boilerplate.config import config
from aiohttp_boilerplate.dbpool import pg as db
from aiohttp_boilerplate.log import sql_logger
from aiohttp_boilerplate.sql import consts


class SQLException(Exception):
    pass


class SQL(object):

    def __init__(self, table, conn=None, logger=sql_logger):
        self.conn = conn
        self.table = table
        self.query = ''
        self.params = {}
        self.logger = logger

    def __str__(self) -> str:
        return "{} {} {} {}".format(
            self.conn,
            self.table,
            self.query,
            self.params,
        )

    async def get_connection(self):
        if self.conn is None:
            try:
                self.conn = await dbpool.DB_POOL.acquire()
            except Exception:
                loop = asyncio.get_event_loop()
                db.DB_POOL = await db.create_pool(config['postgres'], loop=loop)
                self.conn = await db.DB_POOL.acquire()
        return self.conn

    def prepare_where(self, where: str, params: dict, index: int = 0) -> str:
        for i, key in enumerate(params.keys()):
            where = where.replace('{{{}}}'.format(key), '${}'.format(i + index + 1))

        missing_params = re.findall(r'{.*}', where)
        if len(missing_params) > 0:
            raise SQLException('Missing parameters {}'.format(','.join(missing_params)))

        return where

    async def release(self):

        if self.conn:
            await dbpool.DB_POOL.release(self.conn)
            self.conn = None

    async def execute(self, query, params, fetch_method=consts.EXECUTE):
        self.query = query
        self.params = params

        await self.get_connection()

        self.logger.debug(f'query: %s, values: %s', self.query, self.params.values())

        try:
            if fetch_method == consts.EXECUTE:
                result = await self.conn.execute(self.query, *self.params.values())
            elif fetch_method == consts.FETCH:
                result = await self.conn.fetch(self.query, *self.params.values())
            elif fetch_method == consts.FETCHROW:
                result = await self.conn.fetchrow(self.query, *self.params.values())
            elif fetch_method == consts.FETCHVAL:
                result = await self.conn.fetchval(self.query, *self.params.values())
        finally:
            await self.release()

        return result

    async def select(self, fields='*', join='', where='', order='', limit='', params=None, many=False):
        params = params or {}

        if self.table is None:
            raise SQLException('table is not set')

        if type(params) != dict:
            raise SQLException('params have to be dict')

        self.params = params
        # FIXME
        self.query = 'select {} from {}'.format(fields, self.table)  # nosec

        if join:
            _join = ' {}'
            if 'join' not in join.lower():
                _join = ' join {}'
            self.query += _join.format(join)

        if where:
            self.query += ' where {}'.format(self.prepare_where(where, params))

        if order:
            self.query += ' order by {}'.format(order)

        if limit:
            self.query += ' limit {}'.format(limit)

        await self.get_connection()

        self.logger.debug(f'query: %s, values: %s', self.query, self.params.values())

        if config.get('TRACEBACK', 0) > 0:
            import traceback
            self.logger.warning('\n'.join([str(line) for line in traceback.extract_stack()]))

        try:
            stmt = await self.conn.prepare(self.query)
            if many:
                result = await stmt.fetch(*self.params.values())
            else:
                result = await stmt.fetchrow(*self.params.values())
        finally:
            await self.release()

        return result

    async def insert(self, data: dict) -> int:
        on_conflict = data.pop('__on_conflict', '')
        self.query = 'insert into {}({}) values({}) {} RETURNING id'.format(
            self.table,
            ','.join(data.keys()),
            ','.join(['$%d' % (x + 1) for x in range(0, data.__len__())]),
            on_conflict
        )
        # self.params = self._prepare_fields(params)

        await self.get_connection()

        self.logger.debug(f'query: %s, values: %s', self.query, data.values())

        try:
            result = await self.conn.fetchval(self.query, *data.values())
        finally:
            await self.release()

        return result

    async def update(self, where: str, params: dict, data: dict) -> int:
        self.query = 'update {}'.format(self.table)

        if data:
            self.query += ' set '
            self.query += ','.join([key + '=$%d' % (i + 1) for i, key in enumerate(data.keys())])
        if where:
            self.query += ' where {}'.format(self.prepare_where(where, params, len(data)))

        self.params = data
        self.params.update(params)
        # self.params = self._prepare_fields(self.params)

        await self.get_connection()

        self.logger.debug(f'query: %s, values: %s', self.query, self.params.values())

        try:
            result = await self.conn.execute(self.query, *self.params.values())
        finally:
            await self.release()

        return int(result.replace('UPDATE ', ''))

    async def delete(self, where: str, params: dict) -> int:
        # FIXME
        self.query = 'delete from {}'.format(self.table)  # nosec

        if where:
            self.query += ' where {}'.format(self.prepare_where(where, params))

        self.params = params

        await self.get_connection()

        self.logger.debug(f'query: %s, values: %s', self.query, self.params.values())

        try:
            result = await self.conn.execute(self.query, *params.values())
        finally:
            await self.release()

        return int(result.replace('DELETE ', ''))

    async def get_count(self, where: str, params: dict) -> int:
        # FIXME
        self.query = 'select count(*) as count from {}'.format(self.table)  # nosec

        if where:
            self.query += ' where {}'.format(self.prepare_where(where, params))

        self.params = params

        await self.get_connection()

        self.logger.debug(f'query: %s, values: %s', self.query, self.params.values())

        try:
            result = await self.conn.fetchval(self.query, *params.values())
        finally:
            await self.release()

        return result

    async def is_exists(self, where: str, params: dict) -> bool:

        await self.get_connection()
        # FIXME
        query = "SELECT 1 as t FROM {} WHERE {}".format(  # nosec
            self.table,
            self.prepare_where(where, params)
        )

        self.query = query
        self.params = params

        self.logger.debug(f'query: %s, values: %s', self.query, self.params.values())

        try:
            result = await self.conn.fetchval(self.query, *self.params.values())

            if result is None:
                result = False
            else:
                result = True

        finally:
            await self.release()

        return result
