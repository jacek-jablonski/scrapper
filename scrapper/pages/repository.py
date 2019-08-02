from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient

from .models import Page, Task


class PagesRepository:
    def __init__(self, mongo_host: str, mongo_port: int):
        self._mongo = AsyncIOMotorClient(mongo_host, mongo_port)
        self._db = self._mongo.scrapper
        self._tasks_collection = self._db["tasks"]
        self._pages_collection = self._db["pages"]

    async def upsert_task(self, task: Task):
        task_data = task.to_primitive()
        task_id = task_data.pop("_id")
        await self._tasks_collection.replace_one({"_id": task_id}, task_data, upsert=True)

    async def get_task(self, task_id: str) -> Optional[Task]:
        task_data = await self._tasks_collection.find_one({"_id": task_id})
        return Task(task_data) if task_data else None

    async def put_page(self, page: Page):
        await self._pages_collection.insert_one(page.to_primitive())

    async def get_page(self, page_id: str) -> Optional[Page]:
        page_data = await self._pages_collection.find_one({"_id": page_id})
        return Page(page_data) if page_data else None

    def close(self):
        self._mongo.close()
