from dataclasses import asdict, dataclass

from models import Crawler
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from core.db import DB
from typing import List, Dict
from pydantic import UUID4
from core.api_service import ApiService, InsertResponse
from core.aio_kafka import AioProducer
from core import config_loader as config_loader

config = config_loader.Config()
logger = logging.getLogger(__name__)
db = DB()


@dataclass
class CrawlRequestMessage:
    id: str
    html_url: str


class CrawlerRequestService(ApiService):
    def __init__(self):
        super().__init__(entity_model=Crawler)

    async def save_crawler(self, html_url: str) -> InsertResponse:
        async with AsyncSession(db.db_engine) as async_session:
            async with async_session.begin():
                logger.info(f"Save crawler for {html_url}")
                res = await self.insert_entity(async_session, html_url=html_url)
                # produce crawl-request message ( Accepted )  with the generated ( from DB ) crawl id
                # We will wait to Kafka ACK before let the client ACK.
                await AioProducer().produce_message_and_wait_for_ack(
                    config.get(config_loader.CRAWLER_REQUEST_TOPIC),
                    asdict(
                        CrawlRequestMessage(id=str(res.get("id")), html_url=html_url)
                    ),
                )

                # if error occurred id is wasted, no harm
                return res

    async def get_crawler_by_id(self, crawler_id: UUID4) -> Dict:
        async with AsyncSession(db.db_engine) as async_session:
            async with async_session.begin():
                crawler = await self.get_entity_by_id(async_session, crawler_id)
                crawler = DB.row_to_dict(crawler)
                return crawler

    async def get_all_crawlers(self) -> List[Dict]:
        async with AsyncSession(db.db_engine) as async_session:
            async with async_session.begin():
                crawlers = await self.get_entities(async_session)
                crawlers = DB.rows_to_list_of_dict(crawlers)
                return crawlers
