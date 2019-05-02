import ujson
from typing import Mapping

import aiohttp
import jwt

from aiohttp_boilerplate.config import config
from aiohttp_boilerplate.views.exceptions import JSONHTTPError

CLAIM_FIELDS = ['user_id', 'email', 'is_superuser', 'is_staff']


async def validate_token(token: str) -> Mapping:
    _token = token
    if len(token.split(' ')) == 2:
        _, _, _token = token.partition(' ')

    if token is None or len(token) < 100:
        raise JSONHTTPError(
            {"__error__": "Authentication"},
            aiohttp.web.HTTPUnauthorized,
        )

    headers = {'Authorization': token}
    async with aiohttp.ClientSession(json_serialize=ujson, headers=headers) as session:
        async with session.get(config['AUTH_URL']) as resp:
            if resp.status != 204 and resp.status != 200:
                raise JSONHTTPError(
                    {"__error__": "Invalid key"},
                    aiohttp.web.HTTPForbidden,
                )

            claims = {}
            for k, v in encode_token(_token).items():
                for f in CLAIM_FIELDS:
                    if k.endswith(f):
                        claims[f] = v

            return claims


def encode_token(token):
    return jwt.decode(token, verify=False)


class Auth:
    def __init__(self):
        self.user = {}

    async def auth_user(self, is_superadmin=False):
        self.user = await validate_token(
            self.request.headers.get('Authorization', '')
        )

        if is_superadmin:
            await self.check_permission()

    async def try_auth_user(self):
        if not hasattr(self, 'user'):
            try:
                await self.auth_user()
            except (aiohttp.web.HTTPUnauthorized, aiohttp.web.HTTPForbidden):
                pass
        return hasattr(self, 'user')

    async def is_user(self):
        return await self.try_auth_user()

    async def is_admin(self):
        if await self.try_auth_user():
            return self.user.get('is_superuser', False)
        return False

    async def check_permission(self):
        if not await self.is_admin():
            raise JSONHTTPError({'error': 'Forbidden'}, aiohttp.web.HTTPForbidden)
