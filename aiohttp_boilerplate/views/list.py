import warnings

from .retrieve import RetrieveView


class ListView(RetrieveView):

    def __init__(self, request):
        super().__init__(request)
        self.objects = self.get_objects()
        self.limit = self.get_limit()
        self.order = self.get_order()
        self.count = None

    # Return model object
    def get_model(self):
        warnings.warn('Redefine get_schema in inherited class', RuntimeWarning)
        return None

    # Return objects list
    def get_objects(self):
        return self.get_model()(is_list=True)

    # Return limit for sql query
    def get_limit(self):
        # TODO
        # Create consts for default limit amount
        return self.request.query.get('limit', 50)

    # Return order
    def get_order(self):
        return ''

    def join_beautiful_output(self, aliases, data):

        beautiful_data = []
        for row in data:
            temp = super().join_beautiful_output(aliases, row)
            beautiful_data.append(temp)

        return beautiful_data

    async def perform_get(self, fields="", where="", order="", limit=50, params=None):
        # ToDo
        # Can we do this without if/else, just always run join_prepare/beautiful_fields?
        if self.schema_have_joins():
            aliases, fields = self.join_prepare_fields(fields)
            raw_data = await self.objects.sql.select(
                fields=fields,
                where=where,
                order=order,
                limit=limit,
                params=params,
                many=True,
            )
            self.objects.set_data(self.join_beautiful_output(aliases, raw_data))
        else:
            await self.objects.select(
                fields=fields,
                where=where,
                order=order,
                limit=limit,
                params=params,
            )

    async def perform_get_count(self, where, params):
        return await self.objects.sql.get_count(where=where, params=params)

    async def get_count(self, where='', params=None):
        params = params or {}
        if self.count is None:
            self.count = await self.perform_get_count(where, params)
        return self.count

    async def get_data(self, objects):
        data = []
        for obj in objects:
            data.append(await super().get_data(obj))

        return data

    async def _get(self):
        await self.on_start()

        await self.before_get()
        await self.perform_get(
            fields=self.fields,
            where=self.where,
            limit=self.limit,
            order=self.order,
            params=self.params,
        )
        await self.after_get()

        return {
            'data': await self.get_data(self.objects.data),
            'count': await self.get_count(
                where=self.where,
                params=self.params,
            )
        }

    async def get(self):
        return self.json_response(await self._get())
