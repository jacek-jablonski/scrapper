from datetime import datetime
from enum import Enum
from uuid import uuid4

from schematics.models import Model
from schematics import types


class Page(Model):
    _id = types.UUIDType(required=True, default=uuid4)
    created_at = types.UTCDateTimeType(required=True, default=datetime.utcnow)
    url = types.URLType(required=True)
    body = types.StringType(required=True)


class TaskStatus(Enum):
    PENDING = "pending"
    FETCHING = "fetching"
    DONE = "done"
    ERROR = "error"


class Task(Model):
    _id = types.UUIDType(required=True, default=uuid4)
    created_at = types.UTCDateTimeType(required=True, default=datetime.utcnow)
    url = types.URLType(required=True)
    status = types.StringType(required=True, default=TaskStatus.PENDING.value)
    error_message = types.StringType(required=False)
    page_id = types.UUIDType(required=False)
