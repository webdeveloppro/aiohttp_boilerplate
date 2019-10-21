from aiohttp import web

from .options import ObjectView
from .exceptions import JSONHTTPError


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
    async def perform_get(self, fields="*", where="", params=None):
        if self.schema_have_joins():
            aliases, fields = self.join_prepare_fields(fields)
            raw_data = await self.obj.sql.select(
                fields=fields,
                where=where,
                params=params,
            )
            self.obj.set_data(self.join_beautiful_output(aliases, raw_data))
        else:
            await self.obj.select(fields=fields, where=where, params=params)

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
        return self.json_response(await self._get())
