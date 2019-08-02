import pytest

from schematics.exceptions import DataError

from .models import Page, Task, TaskStatus


def test_task_model():
    task = Task()
    assert len(str(task._id)) == 36
    assert task.status == TaskStatus.PENDING.value

    with pytest.raises(DataError):
        task.validate()

    task.url = "invalid"
    with pytest.raises(DataError):
        task.validate()

    task.url = "http://www.google.pl"
    task.validate()

    task_data = task.to_primitive()
    assert all(item in task_data for item in ("_id", "created_at", "status", "error_message", "page_id", "url"))


def test_page_model():
    page = Page()
    assert len(str(page._id)) == 36

    with pytest.raises(DataError):
        page.validate()

    page.url = "http://www.google.pl"
    page.body = "somecontent"
    page.validate()
