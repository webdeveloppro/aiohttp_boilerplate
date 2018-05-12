from aiohttp import web

from .options import ObjectView
from .exceptions import JSONHTTPError


class UpdateView(ObjectView):

    def __init__(self, request):
        super().__init__(request)

        self.partial = True
        self.where = ''
        self.params = {}
        self.data = {}

    async def validate(self, data):
        """ Override that method for validation
        """
        return data

    async def perform_update(self, where, params, data):
        return await self.obj.update(where, params, data)

    async def before_update(self):
        pass

    async def after_update(self, data):
        pass

    async def _patch(self):

        await self.on_start()
        # data schema checking
        self.obj.data['id'] = await self.get_id()

        data = {}
        if self.schema:
            data = await self.get_schema_data(partial=self.partial)
        else:
            data = await self.get_request_data(to_json=True)

        if len(data) == 0:
            return JSONHTTPError({'error': 'No content'})

        try:
            self.data = await self.validate(data)
        except Exception as e:
            # ToDo
            # Add logger
            return JSONHTTPError({'error': e})

        await self.before_update()
        try:
            updated = await self.perform_update(
                where=self.where,
                params=self.params,
                data=self.data,
            )
            if updated == 0:
                return JSONHTTPError({'error': 'No object updated'})

        except Exception as e:
            # ToDo
            # Add logger
            return JSONHTTPError(
                {'error': str(e)},
                web.HTTPInternalServerError
            )

        await self.after_update(self.data)
        data = await self.get_data(self.obj.data)
        return self.json_response(data)

    async def _put(self):
        self.partial = False
        return await self.patch()

    async def patch(self):
        return await self._patch()

    async def put(self):
        return await self._put()
