import asyncio

from .models import TaskStatus
from scrapper.processors.sample_processor import UpperizationProcessor
from .services import PagesService


async def test_page_service_fetches_webpage_when_webpage_is_ok(pages_service: PagesService, body):
    url = "http://127.0.0.1/get200"
    task_id = await pages_service.create_fetching_task(url)
    task = await pages_service.get_task(task_id)

    assert str(task._id) == task_id
    assert task.url == url
    assert task.status == TaskStatus.PENDING.value

    # wait for download task to finish
    await asyncio.wait([task for task in asyncio.all_tasks() if task != asyncio.current_task()])
    # fetch task again
    task = await pages_service.get_task(task_id)
    assert task.status == TaskStatus.DONE.value
    page_id = task.page_id
    page = await pages_service.get_page(str(page_id))
    assert page.url == url
    assert page.body == body


async def test_page_service_marks_task_with_error_when_webpage_returns_error(pages_service: PagesService):
    url = "http://127.0.0.1/get400"
    task_id = await pages_service.create_fetching_task(url)
    task = await pages_service.get_task(task_id)

    assert str(task._id) == task_id
    assert task.url == url
    assert task.status == TaskStatus.PENDING.value

    # wait for download task to finish
    await asyncio.wait([task for task in asyncio.all_tasks() if task != asyncio.current_task()])
    # fetch task again
    task = await pages_service.get_task(task_id)
    assert task.status == TaskStatus.ERROR.value
    assert task.page_id is None


async def test_page_service_processes_webpages_with_processor(pages_service: PagesService, body):
    url = "http://127.0.0.1/get200"
    pages_service.set_processors([UpperizationProcessor()])
    task_id = await pages_service.create_fetching_task(url)
    task = await pages_service.get_task(task_id)

    # wait for download task to finish
    await asyncio.wait([task for task in asyncio.all_tasks() if task != asyncio.current_task()])
    # fetch task again
    task = await pages_service.get_task(task_id)
    assert task.status == TaskStatus.DONE.value
    page_id = task.page_id
    page = await pages_service.get_page(str(page_id))
    assert page.body == body.upper()
