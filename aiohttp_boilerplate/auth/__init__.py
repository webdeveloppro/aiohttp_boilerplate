from typing import Mapping

import aiohttp
import jwt
import ujson

from aiohttp_boilerplate import config
from aiohttp_boilerplate.views.exceptions import JSONHTTPError


async def validate_token(headers: dict) -> Mapping:
    async with aiohttp.ClientSession(json_serialize=ujson, headers=headers) as session:
        cfg = await config.load_config()
        async with session.get(cfg['AUTH_URL']) as resp:
            if resp.status != 204 and resp.status != 200:
                raise JSONHTTPError(
                    {"__error__": "Invalid key"},
                    aiohttp.web.HTTPForbidden,
                )
            # ToDo
            # Check if user expired
            return await resp.json()


# ToDo
# Verify this method
def encode_token(token):
    return jwt.decode(token, verify=False)


class Auth:
    def __init__(self):
        self.auth = {}

    async def auth_user(self, check_permissions=False):
        token = self.request.headers.get('Authorization', '')
        headers = {'Authorization': token}
        if token == '':
            token = self.request.headers.get('X-Session-Token', '')
            headers = {'X-Session-Token': token}
        if token == '':
            token = self.request.headers.get('Cookie', '')
            headers = {'Cookie': token}
        self.request.log.debug('%s %s', config['AUTH_URL'], headers)
        self.auth = await validate_token(headers)

        if check_permissions:
            await self.check_permission()

    async def check_permission(self):
        pass
