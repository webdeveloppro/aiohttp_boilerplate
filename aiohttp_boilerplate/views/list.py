import warnings

from .retrieve import RetrieveView

ALLOW_ORDER = ["asc", "desc"]


class ListView(RetrieveView):
    order_fields = []
    order_default = ''
    order_map_table = {}
    order_key = 'order'

    limit_default = 50
    limit_max_default = 100

    def __init__(self, request):
        super().__init__(request)
        self.objects = self.get_objects()
        self.limit = self.get_limit()
        self.order = self.get_order()
        self.offset = self.get_offset()
        self.count = None

    # Return model object
    def get_model(self):
        warnings.warn('Redefine get_schema in inherited class', RuntimeWarning)
        return None

    # Return objects list
    def get_objects(self):
        return self.get_model()(is_list=True, db_pool=self.request.app.db_pool)

    @staticmethod
    def str_to_int(value: str):
        try:
            value = int(value)
        except (ValueError, TypeError):
            value = None
        return value

    # Return limit for sql query
    def get_limit(self):
        limit = self.str_to_int(
            self.request.query.get('limit', self.limit_default)
        )

        if limit > self.limit_max_default:
            return self.limit_max_default

        return limit

    # Return offset for sql query
    def get_offset(self):
        return self.str_to_int(self.request.query.get("offset"))

    # Return order
    def get_order(self):
        order = self.request.query.get(self.order_key, "")
        prepared_order = self.order_default
        if not order:
            return prepared_order

        field, f_order = order, "desc"
        if ":" in order:
            field, f_order = order.split(":")

        if field in self.order_fields and f_order in ALLOW_ORDER:
            prepared_order = f"{field} {f_order}"
            table_alias = self.order_map_table.get(field, "t0")
            if table_alias:
                prepared_order = table_alias + "." + prepared_order

        return prepared_order

    def join_beautiful_output(self, aliases, data):

        beautiful_data = []
        for row in data:
            temp = super().join_beautiful_output(aliases, row)
            beautiful_data.append(temp)

        return beautiful_data

    async def perform_get(self, fields="", **kwargs):
        aliases, fields = self.join_prepare_fields(fields)
        raw_data = await self.objects.sql.select(
            fields=fields, many=True, **kwargs
        )
        self.objects.set_data(self.join_beautiful_output(aliases, raw_data))

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
            offset=self.offset,
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
