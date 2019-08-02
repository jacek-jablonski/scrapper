from json.decoder import JSONDecodeError

from aiohttp import web
from schematics import exceptions as schematics_exceptions
from schematics import types
from schematics.models import Model

from .models import TaskStatus


class PageFetchRequest(Model):
    url = types.URLType(required=True)


def get_pages_service(request):
    return request.app["pages_service"]


async def pages_get(request):
    page_id = request.match_info["page_id"]
    pages_service = get_pages_service(request)
    page = await pages_service.get_page(page_id)
    if page is None:
        raise web.HTTPNotFound()
    return web.json_response(page.to_primitive())


async def pages_post(request):
    try:
        data = await request.json()
        page_fetch_request = PageFetchRequest(data)
        page_fetch_request.validate()
    except JSONDecodeError:
        raise web.HTTPBadRequest(reason="Invalid JSON payload")
    except schematics_exceptions.DataError as ex:
        raise web.HTTPBadRequest(reason=ex.to_primitive())

    pages_service = get_pages_service(request)
    task_id = await pages_service.create_fetching_task(page_fetch_request.url)
    task_url = request.app.router["tasks-get"].url_for(task_id=str(task_id))
    return web.HTTPAccepted(headers={"Location": str(task_url)})


async def tasks_get(request):
    pages_service = get_pages_service(request)
    task_id = request.match_info["task_id"]
    task = await pages_service.get_task(task_id)
    if task is None:
        raise web.HTTPNotFound()
    if task.status == TaskStatus.DONE.value:
        return web.HTTPSeeOther(location=request.app.router["pages-get"].url_for(page_id=str(task.page_id)))
    task_data = task.to_primitive()
    del task_data["page_id"]
    return web.json_response(task_data)
