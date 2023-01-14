from aiohttp import web

from aiohttp_boilerplate.views import fixed_dump
from aiohttp_boilerplate.views.exceptions import JSONHTTPError
from aiohttp_boilerplate.sql import SQL


class Manager:

    def __init__(self, db_pool, is_list=False, storage=None):
        self.is_list = is_list
        self.db_pool = db_pool

        # ToDo
        # Rename to self.get_table()
        self.table = self.__table__  + """ as t0 """

        if is_list:
            self.data = []
        else:
            self.data = {}

        self.set_storage(self.table, storage, self.db_pool)

    def set_storage(self, table, storage, db_pool):
        '''
        Will set a storage for model
        Can me postgresql/reddis/anything else
        '''
        if storage is None:
            storage = SQL
        self.sql = storage(table, db_pool)

    def __getattribute__(self, key):
        try:
            return super().__getattribute__(key)
        except AttributeError as err:
            if key != 'data':
                if hasattr(self, 'data') is True:
                    if key in self.data:
                        return self.data[key]
                    else:
                        return None

            raise AttributeError(str(err)) from err

    def __setattr__(self, key, value):

        if key in ['table', 'sql', 'is_list', 'data', 'db_pool']:
            return super().__setattr__(key, value)

        if hasattr(self, 'is_list') and self.is_list is True:
            raise Exception('You cannot add proporties for a list')

        # if we created data as a dict or array
        if hasattr(self, 'data') is True:
            if key in self.data:
                self.data[key] = value
            else:
                raise Exception(f"{key} property does not exist, please use "
                                "set_data function first")
        else:
            super().__setattr__(key, value)

    def set_data(self, data=None):

        data = data or {}

        if type(data) != dict and hasattr(data, '__class__') is False:
            raise Exception('data should always be a dict or asyncpg Record class')

        if self.is_list:
            for record in data:
                # new_obj = {}  # not sure  self.__class__()
                new_obj = self.__class__(db_pool=self.db_pool)
                new_obj.set_data(dict(record))
                self.data.append(new_obj)
        else:
            self.data.update(data)

    async def get_by_id(self, id, fields="*"):

        if fields != '*' and 'id' not in fields.split(','):
            fields = 'id,{}'.format(fields)

        await self.select(fields=fields, where='id={id}', params={'id': id})

        # ToDo
        # What if we are using this for the list?
        # we should just return count of objects returned by select
        if self.id is None:
            raise JSONHTTPError(
                {'error': f'Object {self.__class__.__name__} not found by get_by_id'},
                web.HTTPNotFound,
            )

        return self

    async def get_by(self, fields="*", **filters):
        """
            SELECT with AND statement
        Example:
            user = await User.get_by(
                email='XXX'
                first_name='YYY'
            )
        if len(filters.keys()) == 0:
            raise Exception('Select cannot be empty')
        """

        if fields != '*' and 'id' not in fields.split(','):
            fields = f'id,{fields}'

        where = ' AND '.join(['{key}={{{key}}}'.format(key=f) for f in filters.keys()])

        await self.select(
            fields=fields,
            where=where,
            params=filters
        )

        # ToDo
        # What if we are using this for the list?
        # we should just return count of objects returned by select
        if self.id is None:
            raise JSONHTTPError(
                {'error': f'Object {self.__class__.__name__} not found by get_by'},
                web.HTTPNotFound,
            )

        return self

    async def select(
        self, fields='*', join='', where='', order='', limit='', offset=None, params=None
    ):
        data = await self.sql.select(
            fields=fields, join=join, where=where, order=order, limit=limit, offset=offset,
            params=params, many=self.is_list
        )
        self.set_data(data)
        # ToDo
        # select should return length of returned objects from db
        return self

    async def insert(self, data=None, load=0, **kwargs):
        data = data or {}

        data.update(kwargs)
        self.set_data(data)

        raw_result = await self.sql.insert(data=data)
        self.set_data(raw_result)

        if load == 1:
            await self.select(where='id={id}', params={'id': self.id})

        # ToDo
        # insert should return length amount of effected row
        return self

    async def update(self, where='', params=None, data=None, **kwargs):
        """
            Example:
                user = await User.get_by_id(5)
                user.update(
                    last_login = datetime.now()
                )
                await User().update(
                    where="email={email} and first_name={f}",
                    params={'email': 'XXX', 'f': 'YYY'}
                    data={'first_name': 'NEW NAME'}
                )
        """
        data = data or {}
        params = params or {}
        data.update(kwargs)

        if where == '':
            if self.id is None:
                raise Exception('id is empty dont know how to update')
            where = "id={id}"
            params = {'id': self.id}

        updated = await self.sql.update(where=where, params=params, data=data)
        self.set_data(data)
        return updated

    async def delete(self, where='', params=None):
        params = params or {}
        if self.is_list is False and self.id:
            where = where + ' id={id}'
            params['id'] = self.id
        elif self.is_list:
            where = where + 'id in ({ids})'
            params['ids'] = self.list.get_ids()

        deleted = await self.sql.delete(where=where, params=params)
        if self.is_list:
            self.data = []
        else:
            self.data = {}
        return deleted

    async def get_count(self, where='', params=None):

        return await self.sql.get_count(where=where, params=params)

    async def is_exists(self, where='', params=None, **kwargs):
        params = params or {}
        params.update(kwargs)
        new_params = params.copy()
        return await self.sql.is_exists(where, new_params)


class JsonbManager(Manager):
    # ToDo
    # Add validation key_name is not None
    __key_name__ = None
    __update_type__ = 'update'

    async def select(self, fields='*', where='', order='', limit='', params=None):

        if fields == '*':
            fields = self.__key_name__
        data = await self.sql.select(fields=fields, where=where, order=order, limit=limit,
                                     params=params, many=False)

        # ToDo
        # Add other fields to the team_members level
        if data and self.__key_name__ in data:
            self.set_data(data[self.__key_name__])
        else:
            raise Exception('{"status": "No object updated"}')
        return self.data

    async def insert(self, where, params, data):
        # ToDo
        # check where is not empty
        # ToDo
        # check __update_type_ is not empty and valid

        data = fixed_dump(data)
        query = "update {table} set {key}="
        if self.__update_type__ == 'append':
            query += "jsonb_set({key}, concat('{{',"
            query += " jsonb_array_length({key}),'}}')::text[], '{data}'::jsonb) "
        elif self.__update_type__ == 'update':
            query += "'{data}'::jsonb"

        query += ' where {where} RETURNING '
        
        if self.__update_type__ == 'append':
            query += 'jsonb_array_length({key}) as r'
        elif self.__update_type__ == 'update':
            query += 'id'
        query = query.format(
            table=self.table,
            key=self.__key_name__,
            data=data.replace("'", "\'"),
            where=self.sql.prepare_where(where, params)
        )

        result = await self.sql.execute(query, params)
        result = int(result.replace('UPDATE ', ''))
        if result == 0:
            raise Exception('{"status": "No object updated"}')
        return result

    async def update(self, where, params, data):

        # Without INDEX we can do only INSERT
        # With INDEX we will do UPDATE
        if 'index' not in params.keys():
            return await self.insert(where, params, data)

        # ToDo
        # check where is not empty
        data = fixed_dump(data)

        # FIXME
        query = "UPDATE \
            {table} set {key}=jsonb_set({key}, '{{{index}}}', '{data}'::jsonb) ".format(  # nosec
            table=self.table,
            key=self.__key_name__,
            data=data.replace("'", ""),
            index=params['index']
        )
        del params['index']

        query += ' where {where} RETURNING jsonb_array_length({key}) as r'.format(
            key=self.__key_name__,
            where=self.sql.prepare_where(where, params)
        )

        result = await self.sql.execute(query, params)
        result = int(result.replace('UPDATE ', ''))
        return result

    async def delete(self, where, params):
        # FIXME
        query = "UPDATE {table} SET {key}={key}::jsonb-{index} ".format(  # nosec
            table=self.table,
            key=self.__key_name__,
            index=params['index'],
        )
        del params['index']
        query += "WHERE {where} RETURNING 1 as r".format(
            where=self.sql.prepare_where(where, params)
        )

        result = await self.sql.execute(query, params)
        return int(result.replace('UPDATE ', ''))
