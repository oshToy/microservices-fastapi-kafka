import aiokafka
from models import CrawlerStatus
from core.core_models import Status
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from core.db import DB
from typing import Dict, Union, List
from pydantic import UUID4
from core.api_service import ApiService, InsertResponse
from datetime import datetime
from sqlalchemy.sql.dml import DMLWhereBase

logger = logging.getLogger(__name__)
db = DB()


class CrawlStatusMessageValue:
    def __init__(
        self, status: Status, create_at: Union[str, None] = None, file_path: str = None
    ):
        self.status: Status = status
        self.file_path: Union[str, None] = file_path
        self.create_at: datetime = create_at
        self.allowed_prev_statuses: List[Status] = status

    @property
    def create_at(self) -> datetime:
        return self._create_at

    @create_at.setter
    def create_at(self, str_time: Union[str, None]):
        if not str_time:
            self._create_at: datetime = datetime.utcnow()
        else:
            self._create_at: datetime = datetime.fromisoformat(str_time)

    @property
    def allowed_prev_statuses(self) -> List[Status]:
        return self._allowed_prev_statuses

    @allowed_prev_statuses.setter
    def allowed_prev_statuses(self, status: Status):
        self._allowed_prev_statuses = CrawlStatusService.get_allowed_prev_statuses(
            status
        )

    def to_update_dict(self):
        update_dict = {"status": self.status, "update_at": self.create_at}
        if self.file_path:
            update_dict["file_path"] = self.file_path
        return update_dict


class CrawlStatusService(ApiService):
    def __init__(self):
        super().__init__(entity_model=CrawlerStatus)
        self.entity_model: CrawlerStatus = self.entity_model

    #  add where statement that allow only legal update ( A -> R -> E/C ) = idempotency
    @staticmethod
    def get_allowed_prev_statuses(status: Status) -> List[Status]:
        if status == Status.Accepted.value:
            return []
        elif status == Status.Running.value:
            return [Status.Accepted.value]
        elif status in {Status.Complete.value, Status.Error.value}:
            return [Status.Accepted.value, Status.Running.value]

    async def save_crawler_status(
        self,
        status_id: UUID4,
        status: Status = Status.Accepted.value,
    ) -> InsertResponse:
        async with AsyncSession(db.db_engine) as async_session:
            async with async_session.begin():
                logger.info(f"Save crawler status for {status_id}")
                return await self.insert_entity(
                    async_session, id=status_id, status=status
                )

    async def update_crawler_status(
        self,
        status_id: UUID4,
        allowed_prev_statuses: List[Status],
        update_at: datetime = datetime.utcnow(),
        upsert: bool = False,
        **values,
    ) -> InsertResponse:
        async with AsyncSession(db.db_engine) as async_session:
            async with async_session.begin():
                logger.info(f"Update crawler status for {status_id} with {values}")
                logger.info(f"allowed_prev_statuses {allowed_prev_statuses}")
                where_clause = [self.entity_model.status.in_(allowed_prev_statuses)]
                return await self.update_entity(
                    async_session,
                    status_id,
                    where_clauses=where_clause,
                    update_at=update_at,
                    upsert=upsert,
                    **values,
                )

    async def get_crawler_status_by_id(self, status_id: UUID4) -> Dict:
        async with AsyncSession(db.db_engine) as async_session:
            async with async_session.begin():
                status = await self.get_entity_by_id(async_session, status_id)
                return DB.row_to_dict(status)

    async def handle_status_updates(self, msg: aiokafka.ConsumerRecord):
        try:
            status_id: str = msg.key
            logger.info(f"handle_status_updates {status_id}")
            crawler_status: CrawlStatusMessageValue = CrawlStatusMessageValue(
                **msg.value
            )
            logger.info(f"handle_status_updates {status_id, crawler_status.status}")
            if crawler_status.status == Status.Accepted.value:
                return await self.save_crawler_status(
                    status_id=status_id, status=crawler_status.status
                )
            elif crawler_status.status in {
                Status.Running.value,
                Status.Error.value,
                Status.Complete.value,
            }:
                return await self.update_crawler_status(
                    status_id=status_id,
                    allowed_prev_statuses=crawler_status.allowed_prev_statuses,
                    upsert=True,
                    **crawler_status.to_update_dict(),
                )
        except Exception as e:
            logger.error(e.__traceback__)
            logger.error(e)
