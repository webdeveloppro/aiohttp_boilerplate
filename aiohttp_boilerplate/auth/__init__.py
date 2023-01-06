from typing import Mapping

import aiohttp
import jwt
import ujson

from aiohttp_boilerplate.config import config
from aiohttp_boilerplate.logging import get_logger
from aiohttp_boilerplate.views.exceptions import JSONHTTPError

log = get_logger('aiohttp_boilerplate.auth')

async def validate_token(headers: dict) -> Mapping:
    async with aiohttp.ClientSession(json_serialize=ujson, headers=headers) as session:
        async with session.get(config['AUTH_URL']) as resp:
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

    async def auth_user(self, is_superadmin=False):
        token = self.request.headers.get('Authorization', '')
        headers = {'Authorization': token}
        if token == '':
            token = self.request.headers.get('X-Session-Token', '')
            headers = {'X-Session-Token': token}
        if token == '':
            token = self.request.headers.get('Cookie', '')
            headers = {'Cookie': token}
        log.debug('%s %s', config['AUTH_URL'], headers)
        self.auth = await validate_token(headers)

        if is_superadmin:
            await self.check_permission()

    async def try_auth_user(self):
        if not hasattr(self, 'auth'):
            try:
                await self.auth_user()
            except (aiohttp.web.HTTPUnauthorized, aiohttp.web.HTTPForbidden):
                pass
        return hasattr(self, 'auth')

    async def is_user(self):
        return await self.try_auth_user()

    async def is_admin(self):
        if await self.try_auth_user():
            return self.auth.get('is_superuser', False)
        return False

    async def check_permission(self):
        if not await self.is_admin():
            raise JSONHTTPError({'error': 'Forbidden'}, aiohttp.web.HTTPForbidden)
