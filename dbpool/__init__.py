import asyncpg
import re
import json

from aiohttp_boilerplate.views import fixed_dump
from aiohttp_boilerplate.config import CONFIG


# encoder/decoder is needed to work correctly with jsonb fields
def _encoder(value):
    val = bytes(fixed_dump(value).encode('utf-8'))
    val = b'\x01' + val
    return val


def _decoder(value):
    return json.loads(
        re.sub(r'(\n|\t|\x01)', '', value.decode('utf-8'))
    )


async def setup_connection(conn):

    await conn.set_type_codec(
        'jsonb',
        encoder=_encoder,
        decoder=_decoder,
        schema='pg_catalog',
        format='binary',
    )


async def create_connection(config=None, loop=None):

    if config is None:
        config = CONFIG['postgres']

    return await asyncpg.connect(
        **config,
        loop=loop
    )


async def create_pool(config=None, loop=None):

    if config is None:
        config = CONFIG['postgres']

    return await asyncpg.create_pool(
        **config,
        loop=loop,
        setup=setup_connection
    )

# Little trick to get convinient way of working with db connection
# We will assign db pool connection during start appliction and destroy during shutdown
# with db.DB_POOL variable
DB_POOL = None
