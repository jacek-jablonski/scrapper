import asyncio
import pytest

from .app import App
from .pages.models import Page, Task
from .pages.repository import PagesRepository


@pytest.yield_fixture(scope="module")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


class MongoCollectionStub:
    def __init__(self):
        self._db = {}

    async def replace_one(
        self, filter, replacement, upsert=False, bypass_document_validation=False, collation=None, session=None
    ):
        replacement = replacement.copy()
        replacement["_id"] = filter["_id"]
        self._db[filter["_id"]] = replacement

    async def find_one(self, filter):
        return self._db.get(filter["_id"], None)

    async def insert_one(self, document):
        self._db[document["_id"]] = document


@pytest.fixture(scope="module")
def pages_repository():
    pages_repository = PagesRepository("127.0.0.1", 27071)
    pages_repository._tasks_collection = MongoCollectionStub()
    pages_repository._pages_collection = MongoCollectionStub()
    return pages_repository


@pytest.fixture
def cli(pages_repository, aiohttp_client, loop):
    app = App(loop)
    cli = loop.run_until_complete(aiohttp_client(app._app))
    app._app["pages_service"]._pages_repository = pages_repository
    return cli


@pytest.mark.asyncio
async def test_repository_stores_tasks(pages_repository):
    task = Task()
    task_id = task._id
    task.url = "http://www.google.pl"
    await pages_repository.upsert_task(task)
    repository_task = await pages_repository.get_task(str(task_id))
    assert task._id == repository_task._id
    assert task.created_at == repository_task.created_at
    assert task.status == repository_task.status
    assert task.url == repository_task.url


@pytest.mark.asyncio
async def test_repository_stores_pages(pages_repository):
    page = Page()
    page.url = "http://www.google.pl"
    page.body = "test"

    await pages_repository.put_page(page)
    repository_page = await pages_repository.get_page(str(page._id))
    assert page._id == repository_page._id
    assert page.url == repository_page.url
    assert page.body == repository_page.body


async def test_posting_malformed_url_rejects_validation(cli):
    resp = await cli.post("/pages", json={"url": "http:/google.pl"})
    assert resp.status == 400


async def test_posting_valid_url_starts_processing_task(cli):
    url = "http://google.pl"
    resp = await cli.post("/pages", json={"url": url})
    assert resp.status == 202
    assert "Location" in resp.headers
    location = resp.headers["location"]
    for _ in range(10):
        page_resp = await cli.get(location)
        json = await page_resp.json()
        status = page_resp.status
        if status == 200 and "body" in json:
            break
        await asyncio.sleep(1)

    assert status == 200
    assert json["url"] == url
    assert len(json["body"]) > 0
