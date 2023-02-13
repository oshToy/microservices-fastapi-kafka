from models import CrawlerStatus, Status
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from core.db import DB
from typing import Dict, Union
from pydantic import UUID4
from core.api_service import ApiService, InsertResponse

logger = logging.getLogger(__name__)
db = DB()


class CrawlStatusService(ApiService):
    def __init__(self):
        super().__init__(entity_model=CrawlerStatus)
        self.entity_model: CrawlerStatus = self.entity_model

    async def save_crawler_status(
        self,
        status_id: UUID4,
        file_path: Union[str, None],
        status: Status = Status.Accepted.value,
    ) -> InsertResponse:
        async with AsyncSession(db.db_engine) as async_session:
            async with async_session.begin():
                logger.info(f"Save crawler status for {file_path}")
                return await self.insert_entity(
                    async_session, id=status_id, status=status
                )

    async def update_crawler_status(self, status_id: UUID4, **values) -> InsertResponse:
        async with AsyncSession(db.db_engine) as async_session:
            async with async_session.begin():
                logger.info(f"Update crawler status for {status_id} with {values}")
                return await self.update_entity(async_session, status_id, **values)

    async def get_crawler_status_by_id(self, status_id: UUID4) -> Dict:
        async with AsyncSession(db.db_engine) as async_session:
            async with async_session.begin():
                status = await self.get_entity_by_id(async_session, status_id)
                return DB.row_to_dict(status)
