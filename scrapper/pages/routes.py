from aiohttp import web

from .endpoints import pages_get, pages_post, tasks_get


routes = [
    web.get("/pages/{page_id}", pages_get, name="pages-get"),
    web.post("/pages", pages_post, name="pages-post"),
    web.get("/tasks/{task_id}", tasks_get, name="tasks-get"),
]
