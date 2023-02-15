import logging
from abc import ABC
import faust
import config_loader as config_loader
import metrics
from prometheus_client import start_http_server
import aiohttp
from enum import Enum
from typing import Union
from datetime import datetime, timedelta

SERVICE_NAME = "html_crawler"
config = config_loader.Config()

logging.basicConfig(
    level=logging.getLevelName(config.get(config_loader.LOGGING_LEVEL)),
    format=config.get(config_loader.LOGGING_FORMAT),
)

logger = logging.getLogger(__name__)

app = faust.App(SERVICE_NAME, broker=config.get(config_loader.KAFKA_BROKER))


# TODO schema registry
class CrawlRequest(faust.Record, ABC, serializer="json"):
    id: str
    html_url: str


class Status(str, Enum):
    Accepted = "Accepted"
    Running = "Running"
    Error = "Error"
    Complete = "Complete"


# TODO schema registry
class CrawlStatusMessage(faust.Record, ABC, serializer="json", isodates=True):
    id: str
    status: str
    file_path: Union[str, None]
    process_at: datetime
    fetch_at: Union[datetime, None]

    async def produce_status_message(self):
        message = {"status": self.status, "process_at": self.process_at}
        if self.file_path:
            message["file_path"] = self.file_path
        if self.fetch_at:
            message["fetch_at"] = self.fetch_at
        await produce_crawler_status_topic.send(key=self.id, value=message)


src_crawler_request_topic = app.topic(
    config.get(config_loader.SOURCE_CRAWLER_REQUEST_TOPIC), value_type=CrawlRequest
)
produce_crawler_status_topic = app.topic(
    config.get(config_loader.PRODUCE_CRAWLER_STATUS_TOPIC),
    value_type=CrawlStatusMessage,
)

url_cache = app.Table("url_cache")


@app.agent(src_crawler_request_topic)
async def process_crawl_request(requests) -> None:
    session = aiohttp.ClientSession()
    async for request in requests:
        metrics.SOURCE_CRAWLER_REQUEST_RECEIVED_CNT.inc()
        request: CrawlRequest
        logger.info(f"Received new CrawlRequest {request}")
        await CrawlStatusMessage(
            id=request.id, status=Status.Running.value, process_at=datetime.utcnow()
        ).produce_status_message()

        hashed_url = hash(request.html_url)
        file_path = f"./files/{hashed_url}.html"
        is_done = False
        if hashed_url not in url_cache:
            print("hereee")
            is_done = await process_html_file(
                session=session, request=request, file_path=file_path
            )
            if is_done:
                url_cache[hashed_url] = datetime.utcnow()
        else:
            if url_cache[hashed_url] + timedelta(days=7) > datetime.utcnow():
                is_done = True
        if is_done:
            metrics.SOURCE_CRAWLER_REQUEST_COMPLETE_CNT.inc()
            await CrawlStatusMessage(
                id=request.id,
                status=Status.Complete.value,
                process_at=datetime.utcnow(),
                file_path=file_path,
                fetch_at=url_cache[hashed_url],
            ).produce_status_message()


async def process_html_file(
    session: aiohttp.ClientSession, request: CrawlRequest, file_path: str
) -> bool:
    print(request.html_url)
    print(file_path)
    async with session.get(request.html_url) as response:
        try:
            if response.status >= 300:
                raise FileNotFoundError("server exist, but response with error")
            with open(file_path, "w", encoding="utf8") as fp:
                while True:
                    # TODO check if possible to gzip
                    chunk = await response.content.read(8 * 1000)
                    fp.write(chunk.decode())
                    if not chunk:
                        break
        except Exception as e:
            logger.error(e)
            metrics.SOURCE_CRAWLER_REQUEST_FAILED_CNT.inc()
            await CrawlStatusMessage(
                id=request.id,
                status=Status.Error.value,
                process_at=datetime.utcnow(),
            ).produce_status_message()
            return False
        else:
            return True


@app.task
async def on_started() -> None:
    logger.info("Starting prometheus server")
    logger.warning("To start server use command: faust -A main worker -l info")

    start_http_server(port=config.get(config_loader.PROMETHEUS_PORT))
