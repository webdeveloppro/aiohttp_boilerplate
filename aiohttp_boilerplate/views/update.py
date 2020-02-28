from aiohttp import web
from aiohttp_boilerplate.config import config

from .options import ObjectView
from .exceptions import JSONHTTPError


class UpdateView(ObjectView):

    def __init__(self, request):
        super().__init__(request)

        # Can we update a part of schema data
        self.partial = True
        self.where = ''
        self.params = {}
        self.data = {}

    async def validate(self, data: dict) -> dict:
        """ Override that method for custom validation
        """
        return data

    async def perform_update(self, where: str, params: dict, data: dict) -> dict:
        ''' Runs after:
                - successful validation method
                - before_update method
            Calls obj.update function
        '''
        return await self.obj.update(where, params, data)

    async def before_update(self, data: dict) -> dict:
        ''' Runs after:
                - successful validation method
            If you want to change your data before system calls insert method
            Use this method
        '''
        return data

    async def after_update(self, data: dict):
        ''' Runs after:
                - successful validation method
                - before_create method
                - perfom_create method
            If you need to do anything after object updated
            Do it here

            new object data is self.obj
        '''
        pass

    async def _patch(self):
        ''' Post method handler, will run one by one
            - on_start
            - get_schema_data/get_data
            - validate
            - before_update
            - perfomupdate
            - after_update
            - get_data
        '''

        await self.on_start()

        data = {}
        if self.schema:
            data = await self.get_schema_data(partial=self.partial)
        else:
            data = await self.get_request_data(to_json=True)

        if len(data) == 0:
            raise JSONHTTPError({'error': 'No content'})

        try:
            data = await self.validate(data)
        except Exception as e:
            # ToDo
            # Add logger
            if config['DEBUG'] > 0:
                import traceback
                import sys
                print('\n'.join([str(line) for line in traceback.extract_stack()]), file=sys.stderr)
                print("Error: ", e, file=sys.stderr)
            raise JSONHTTPError({'error': e})

        self.data.update(await self.before_update(data))
        try:
            updated = await self.perform_update(
                where=self.where,
                params=self.params,
                data=self.data,
            )
            if updated == 0:
                raise JSONHTTPError({'error': 'No object updated'})

        except Exception as e:
            # ToDo
            # Add logger
            if config['DEBUG'] > 0:
                import traceback
                import sys
                traceback.print_exc(file=sys.stderr)
                # print('\n'.join([str(line) for line in traceback.extract_stack()]), file=sys.stderr)
                print("Error: ", e, file=sys.stderr)

            raise JSONHTTPError(
                {'error': str(e)},
                web.HTTPInternalServerError
            )

        await self.after_update(self.data)
        response = await self.get_data(self.obj.data)
        return self.json_response(response)

    async def _put(self):
        self.partial = False
        return await self.patch()

    async def patch(self):
        return await self._patch()

    async def put(self):
        return await self._put()
