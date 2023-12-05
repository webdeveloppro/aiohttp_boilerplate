import logging
from aiohttp import web

from .options import ObjectView
from .exceptions import JSONHTTPError, log


class CreateView(ObjectView):
    partial = False

    def __init__(self, request):
        super().__init__(request)
        self.data = {}

    async def validate(self, data: dict) -> dict:
        ''' Override that method for custom validation
        '''
        return data

    async def perform_create(self, data: dict) -> int:
        ''' Runs after:
                - successful validation method
                - before_create method
            Calls obj.insert function
        '''
        return await self.obj.insert(data=data)

    async def before_create(self, data: dict) -> dict:
        ''' Runs after:
                - successful validation method
            If you want to change your data before system calls insert method
            Use this method
        '''
        return data

    async def after_create(self, data: dict):
        ''' Runs after:
                - successful validation method
                - before_create method
                - perform_create method
            If you need to do anything after object created
            Do it here

            object id is self.obj.id
        '''
        pass

    async def get_data(self, obj) -> dict:
        ''' Return id of the object '''
        return {'id': obj.id}

    async def _post(self):
        ''' Post method handler, will run one by one
            - on_start
            - get_schema_data/get_data
            - validate
            - before_create
            - perfom_create
            - after_create
            - get_data
        '''

        await self.on_start()

        data = {}
        if self.schema:
            data = await self.get_schema_data(partial=self.partial)
        else:
            data = await self.get_request_data(to_json=True)

        data = await self.validate(data)

        if len(data) == 0:
            raise JSONHTTPError({'error': 'No content'}, web.HTTPBadRequest)

        self.data.update(await self.before_create(data))
        self.obj = await self.perform_create(
            data=self.data,
        )

        await self.after_create(data)
        response = await self.get_data(self.obj)
        return self.json_response(response, 201)

    async def post(self):
        ''' Post logic is in _post method
            You can do here authentication check before if you need
        '''
        log.debug('%s %s', self.request.method, str(self.request.url))
        try:
            return await self._post()
        except Exception as err:
            # show any 4xx errors directly
            if hasattr(err, 'status_code'):
                if err.status_code >= 400 and err.status_code < 500:
                    raise err

            log.error(err, exc_info=True)
            err_msg = 'HTTP Internal Server Error'
            
            if log.level == logging.DEBUG:
                err_msg = str(err)
            
            raise JSONHTTPError(
                {'error': err_msg}, web.HTTPInternalServerError
            ) from err
