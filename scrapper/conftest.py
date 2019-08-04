from collections import defaultdict
from urllib.parse import urlparse

import pytest

from aiohttp import web
from .pages import repository
from .pages import services


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


class MongoDbStub:
    def __init__(self):
        self._collections = defaultdict(MongoCollectionStub)

    def __getitem__(self, name):
        return self._collections[name]


class MongoClientStub:
    def __init__(self, host, port):
        self._dbs = defaultdict(MongoDbStub)

    def __getattr__(self, name):
        return self._dbs[name]

    def close(self):
        pass


@pytest.fixture
def pages_repository(monkeypatch):
    with monkeypatch.context() as m:
        m.setattr(repository, "AsyncIOMotorClient", MongoClientStub)
        yield repository.PagesRepository("test", 12345)


SAMPLE_BODY = "sample body response"


@pytest.fixture
def body():
    return SAMPLE_BODY


async def get200(request):
    return web.Response(text=SAMPLE_BODY)


async def get400(request):
    raise web.HTTPBadRequest()


async def get500(request):
    raise web.HTTPBadRequest()


class WrappedSession:
    def __init__(self, session):
        self._session = session

    def get(self, url):
        path = urlparse(url).path
        return self._session.get(path)

    def post(self, url, data):
        path = urlparse(url).path
        return self._session.post(path, data)

    def close(self):
        return self._session.close()


@pytest.fixture
async def http_session(aiohttp_client):
    app = web.Application()
    app.router.add_get("/get200", get200)
    app.router.add_get("/get400", get400)
    app.router.add_get("/get500", get500)
    session = await aiohttp_client(app)
    yield WrappedSession(session)
    await session.close()


@pytest.fixture
async def pages_service(pages_repository, aiohttp_client, http_session):
    return services.PagesService(pages_repository, http_session)
