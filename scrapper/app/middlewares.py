from aiohttp import web
from pymongo import errors as pymongo_errors


@web.middleware
async def error_middleware(request, handler):
    try:
        response = await handler(request)
        return response
    except web.HTTPError as ex:
        message = ex.reason
        return web.json_response(data={"errors": message}, status=ex.status)
    except pymongo_errors.ServerSelectionTimeoutError:
        return web.json_response(
            data={"errors": "Connection to DB timed out"}, status=web.HTTPGatewayTimeout.status_code
        )
