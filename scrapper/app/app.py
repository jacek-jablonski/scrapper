import asyncio
import logging

import aiohttp

from scrapper import config
from scrapper.pages.repository import PagesRepository
from scrapper.pages.routes import routes as pages_routes
from scrapper.pages.services import PagesService
from .middlewares import error_middleware

from scrapper.processors import Processor


logger = logging.getLogger(__name__)


class App:
    def __init__(self, loop: asyncio.AbstractEventLoop):
        self._loop = loop
        self._app = aiohttp.web.Application(middlewares=[error_middleware], loop=self._loop)
        self._processors = []
        self._app.cleanup_ctx.append(self._init_service)
        self._app.router.add_routes(pages_routes)

    async def _init_service(self, app):
        pages_repository = PagesRepository(config.MONGO_HOST, config.MONGO_PORT)
        timeout = aiohttp.ClientTimeout(total=config.CLIENT_HTTP_TIMEOUT)
        session = aiohttp.ClientSession(timeout=timeout)
        app["pages_service"] = PagesService(pages_repository, session, self._processors)
        yield
        await app["pages_service"].close()

    def add_processor(self, processor: Processor):
        self._processors.append(processor)

    def serve(self):
        host = config.APP_HOST
        port = config.APP_PORT
        logger.info(f"Starting Scrapper server on {host}:{port}")
        aiohttp.web.run_app(self._app, host=host, port=port)
