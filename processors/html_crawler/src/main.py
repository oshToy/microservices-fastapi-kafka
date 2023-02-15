import logging
from abc import ABC
import faust
import config_loader as config_loader
import metrics
from prometheus_client import start_http_server
import aiohttp
from enum import Enum
from typing import Union
from datetime import datetime

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
    create_at: datetime

    async def produce_status_message(self):
        await produce_crawler_status_topic.send(
            key=self.id, value={"status": self.status, "create_at": self.create_at}
        )


src_crawler_request_topic = app.topic(
    config.get(config_loader.SOURCE_CRAWLER_REQUEST_TOPIC), value_type=CrawlRequest
)
produce_crawler_status_topic = app.topic(
    config.get(config_loader.PRODUCE_CRAWLER_STATUS_TOPIC),
    value_type=CrawlStatusMessage,
)


@app.agent(src_crawler_request_topic)
async def process_crawl_request(requests) -> None:
    session = aiohttp.ClientSession()
    async for request in requests:
        metrics.SOURCE_CRAWLER_REQUEST_RECEIVED_CNT.inc()
        request: CrawlRequest
        logger.info(f"Received new CrawlRequest {request}")
        await CrawlStatusMessage(
            id=request.id, status=Status.Running.value, create_at=datetime.utcnow()
        ).produce_status_message()

        async with session.get(request.html_url) as response:
            try:
                with open(f"./files/{request.id}.html", "w", encoding="utf8") as fp:
                    while True:
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
                    create_at=datetime.utcnow(),
                ).produce_status_message()
            else:
                metrics.SOURCE_CRAWLER_REQUEST_COMPLETE_CNT.inc()
                await CrawlStatusMessage(
                    id=request.id,
                    status=Status.Complete.value,
                    create_at=datetime.utcnow(),
                ).produce_status_message()


@app.task
async def on_started() -> None:
    logger.info("Starting prometheus server")
    logger.warning("To start server use command: faust -A main worker -l info")

    start_http_server(port=config.get(config_loader.PROMETHEUS_PORT))
