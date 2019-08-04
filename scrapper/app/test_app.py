import asyncio
import pytest

from . import app


@pytest.fixture
async def cli(pages_service, aiohttp_client, monkeypatch):
    with monkeypatch.context() as m:
        m.setattr(app, "PagesRepository", lambda host, port: None)
        m.setattr(app.aiohttp, "ClientSession", lambda timeout: None)
        m.setattr(app, "PagesService", lambda repository, sessions, processor: pages_service)
        application = app.App(asyncio.get_running_loop())
        cli = await aiohttp_client(application._app)
        yield cli


async def test_getting_unknown_task_results_in_404(cli):
    resp = await cli.get("/tasks/invalid")
    assert resp.status == 404


async def test_posting_malformed_url_rejects_validation(cli):
    resp = await cli.post("/pages", json={"url": "http:/google.pl"})
    assert resp.status == 400


async def test_posting_valid_url_starts_processing_task(cli, body):
    url = "http://127.0.0.1/get200"
    resp = await cli.post("/pages", json={"url": url})
    assert resp.status == 202
    assert "Location" in resp.headers
    location = resp.headers["location"]

    # wait for download task to finish
    await asyncio.wait(asyncio.all_tasks(), return_when=asyncio.FIRST_COMPLETED)
    resp = await cli.get(location)
    json = await resp.json()

    assert resp.status == 200
    assert json["url"] == url
    assert json["body"] == body
