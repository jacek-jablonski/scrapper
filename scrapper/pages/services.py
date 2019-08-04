import asyncio
import logging

from typing import List, Optional

import aiohttp

from .models import Page, Task, TaskStatus
from .repository import PagesRepository
from scrapper.processors import Processor, ProcessorError


logger = logging.getLogger(__name__)


class PagesService:
    def __init__(
        self,
        pages_repository: PagesRepository,
        http_session: aiohttp.ClientSession,
        processors: List[Processor] = list(),
    ):
        self._pages_repository = pages_repository
        self._session = http_session
        self.set_processors(processors)

    async def _process_body(self, body: str) -> str:
        for processor in self._processors:
            body = await processor.run(body)
        return body

    async def _process_task(self, task: Task):
        logger.info(f"Task {task._id} processing started")
        updated_task = Task(task.to_primitive())
        updated_task.status = TaskStatus.FETCHING.value
        await self._pages_repository.upsert_task(updated_task)
        try:
            async with self._session.get(task.url) as resp:
                body = await resp.text()
                status_code = resp.status
                reason = resp.reason
            body = await self._process_body(body)
        except aiohttp.client_exceptions.ClientConnectorError as ex:
            logger.error(f"Error occured when processing task {task._id}")
            updated_task.status = TaskStatus.ERROR.value
            updated_task.error_message = str(ex)
        except asyncio.TimeoutError:
            logger.error(f"Timeout occured in task {task._id}")
            updated_task.status = TaskStatus.ERROR.value
            updated_task.error_message = "Operation timed out"
        except asyncio.CancelledError:
            logger.error(f"Processing task {task._id} cancelled")
            updated_task.status = TaskStatus.ERROR.value
            updated_task.error_message = "Task cancelled"
        except ProcessorError as ex:
            logger.error(f"Processor error occured when processing task {task._id}")
            updated_task.status = TaskStatus.ERROR.value
            updated_task.error_message = ex.message
        else:
            if status_code < 400:
                page = Page()
                page.url = task.url
                page.body = body
                await self._pages_repository.put_page(page)
                updated_task.status = TaskStatus.DONE.value
                updated_task.page_id = page._id
            else:
                updated_task.status = TaskStatus.ERROR.value
                updated_task.error_message = reason
        finally:
            await self._pages_repository.upsert_task(updated_task)
            logger.info(f"Finished processing task {task._id}")

    def set_processors(self, processors: List[Processor] = list()):
        self._processors = list(processors)

    async def create_fetching_task(self, url: str) -> str:
        task = Task()
        task.url = url
        await self._pages_repository.upsert_task(task)
        asyncio.create_task(self._process_task(task))
        return str(task._id)

    async def get_task(self, task_id: str) -> Optional[Task]:
        return await self._pages_repository.get_task(task_id)

    async def get_page(self, page_id: str) -> Optional[Page]:
        return await self._pages_repository.get_page(page_id)

    async def close(self):
        self._pages_repository.close()
        await self._session.close()
