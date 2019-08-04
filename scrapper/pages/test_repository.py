from .models import Page, Task


async def test_my_test(pages_repository):
    task = Task()
    task_id = task._id
    task.url = "http://www.google.pl"
    await pages_repository.upsert_task(task)
    repository_task = await pages_repository.get_task(str(task_id))
    assert task._id == repository_task._id
    assert task.created_at == repository_task.created_at
    assert task.status == repository_task.status
    assert task.url == repository_task.url


async def test_repository_stores_pages(pages_repository):
    page = Page()
    page.url = "http://www.google.pl"
    page.body = "test"
    await pages_repository.put_page(page)
    repository_page = await pages_repository.get_page(str(page._id))
    assert page._id == repository_page._id
    assert page.url == repository_page.url
    assert page.body == repository_page.body
