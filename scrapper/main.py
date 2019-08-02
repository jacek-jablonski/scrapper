import asyncio
import logging

from scrapper.app import App
from scrapper.processors.sample_processor import UpperizationProcessor  # noqa: F401

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.INFO)
    loop = asyncio.get_event_loop()

    app = App(loop)
    # uncomment next line if you want to activate sample processor
    # app.add_processor(UpperizationProcessor())
    app.serve()
