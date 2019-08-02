from __future__ import annotations  # PEP-563

import logging

from abc import ABC, abstractmethod
from typing import Type


logger = logging.getLogger(__name__)


class ProcessorError(RuntimeError):
    def __init__(self, processor_cls: Type[Processor]):
        self.processor_name = processor_cls.__name__
        self.message = f"Error occured in processor {self.processor_name}"


class Processor(ABC):
    async def run(self, body: str) -> str:
        try:
            return await self.process(body)
        except Exception:
            cls = self.__class__
            logger.exception(f"Error occured in {cls.__name__}")
            raise ProcessorError(cls)

    @abstractmethod
    async def process(self, body: str) -> str:
        pass
