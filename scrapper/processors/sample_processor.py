from .processor import Processor


class UpperizationProcessor(Processor):
    async def process(self, body: str) -> str:
        body = body.upper()
        return body
