from models import Crawler
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from db import DB
from sqlalchemy.future import select
from typing import List, Dict
from constants import DB_FETCH_LIMIT
from fastapi import HTTPException
from pydantic import UUID4
from sqlalchemy import insert, column

logger = logging.getLogger(__name__)
db = DB()


class CrawlerRequestService:
    @staticmethod
    async def save_crawler(html_url: str) -> {"id": UUID4}:
        async with AsyncSession(db.db_engine) as session:
            async with session.begin():
                logger.info(f"Save crawler for {html_url}")
                res = await session.execute(insert(Crawler).values(html_url=html_url))
                return {"id": res.inserted_primary_key[0]}

    @staticmethod
    async def get_crawler_by_id(crawler_id: UUID4) -> Dict:
        async with AsyncSession(db.db_engine) as session:
            async with session.begin():
                selected_crawler_execution = await session.execute(
                    select(Crawler).filter(Crawler.id == crawler_id)
                )
                crawler = selected_crawler_execution.scalars().first()
                if not crawler:
                    logger.info(f"crawler not found: {crawler_id}")
                crawler = DB.row_to_dict(crawler)
                if crawler is None:
                    raise HTTPException(status_code=404, detail="crawler not found")
                return crawler

    @staticmethod
    async def get_all_crawlers() -> List[Dict]:
        async with AsyncSession(db.db_engine) as session:
            async with session.begin():
                selected_crawlers_execution = await session.execute(
                    select(Crawler)
                    .order_by(Crawler.create_at.desc())
                    .limit(DB_FETCH_LIMIT)
                )
                selected_crawlers = selected_crawlers_execution.scalars().all()
                crawlers = DB.rows_to_list_of_dict(selected_crawlers)
                return crawlers
