import json
from aiohttp import web


# Sugar for transfer json message to string
def JSONHTTPError(message, errorClass=None, headers={}):
    message = json.dumps(message)
    headers['Content-Type'] = 'application/json'

    if errorClass is None:
        errorClass = web.HTTPBadRequest

    return errorClass(body=message, headers=headers)
