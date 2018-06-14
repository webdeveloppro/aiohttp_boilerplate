import ujson
import aiohttp
import jwt

from aiohttp_boilerplate.views.exceptions import JSONHTTPError
from aiohttp_boilerplate.config import config


async def validate_token(token):

    if token is None or len(token) < 100:
        raise JSONHTTPError(
            {"__error__": "Authentication"},
            aiohttp.web.HTTPUnauthorized,
        )

    headers = {'Authorization': token}
    async with aiohttp.ClientSession(json_serialize=ujson, headers=headers) as session:
        async with session.get(config['AUTH_URL']) as resp:
            if (resp.status != 204 and resp.status != 200):
                raise JSONHTTPError(
                    {"__error__": "Invalid key"},
                    aiohttp.web.HTTPForbidden,
                )
            return encode_token(token)


def encode_token(token):
    return jwt.decode(token, verify=False)
