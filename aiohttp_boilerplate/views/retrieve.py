import logging
from aiohttp import web

from .options import ObjectView
from .exceptions import JSONHTTPError, log


class RetrieveView(ObjectView):

    def __init__(self, request):
        super().__init__(request)
        self.fields = '*'
        self.where = ''
        self.params = {}

    # Will be called before select query to database
    async def before_get(self):
        pass

    # Will be called after select query to database
    async def after_get(self):
        pass

    # Perform database select request
    async def perform_get(self, fields="*", **kwargs):
        aliases, fields = self.join_prepare_fields(fields)
        # id is required for single object
        if fields.rfind("t0.id") == -1:
            fields += ",t0.id as t0__id"
        raw_data = await self.obj.sql.select(fields=fields, **kwargs)
        self.obj.set_data(self.join_beautiful_output(aliases, raw_data))

    # Get request running on start, before get, perfom get and after get functions
    async def _get(self):

        await self.on_start()
        await self.before_get()
        await self.perform_get(
            fields=self.fields,
            where=self.where,
            params=self.params,
        )

        if getattr(self.obj, 'id', None) is None:
            raise JSONHTTPError(
                {"__error__": "No object found"},
                web.HTTPNotFound,
            )

        await self.after_get()
        return await self.get_data(self.obj)

    async def get(self):
        try:
            return self.json_response(await self._get())
        except Exception as err:
            # show any 4xx errors directly
            if hasattr(err, 'status_code'):
                if err.status_code >= 400 and err.status_code < 500:
                    raise err

            log.error(err)
            err_msg = 'HTTP Internal Server Error'
            
            if log.level == logging.DEBUG:
                err_msg = str(err)
            
            raise JSONHTTPError(
                {'error': err_msg}, web.HTTPInternalServerError
            ) from err
