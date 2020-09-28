import asyncpg
import re
import json

from aiohttp_boilerplate.views import fixed_dump
from aiohttp_boilerplate.sql import SQL


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


async def create_connection(conf, loop=None):
    return await asyncpg.connect(
        **conf,
        loop=loop
    )


async def create_pool(conf, loop=None, storage=SQL):
    db_pool = await asyncpg.create_pool(
        **conf,
        loop=loop,
        setup=setup_connection
    )
    storage.init(db_pool)
    return db_pool
