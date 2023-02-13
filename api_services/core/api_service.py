from sqlalchemy import insert
from core.singleton import MetaSingleton
from fastapi import HTTPException
from typing_extensions import TypedDict
from models import BaseEntityModel
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import logging

logger = logging.getLogger(__name__)


class InsertResponse(TypedDict):
    id: UUID4


DB_FETCH_LIMIT = 50


class ApiService(metaclass=MetaSingleton):
    def __init__(self, entity_model: BaseEntityModel):
        self.entity_model: BaseEntityModel = entity_model

    async def insert_entity(
        self, async_session: AsyncSession, **values
    ) -> InsertResponse:
        logger.info(f"Try to Create Entity {values}")
        entity = await async_session.execute(insert(self.entity_model).values(**values))
        return InsertResponse(id=entity.inserted_primary_key[0])

    async def get_entity_by_id(
        self, async_session: AsyncSession, entity_id: UUID4
    ) -> BaseEntityModel:
        selected_entity_execution = await async_session.execute(
            select(self.entity_model).filter(self.entity_model.id == entity_id)
        )
        entity = selected_entity_execution.scalars().first()
        if not entity:
            logger.info(f"entity did not found: {entity_id}")
            raise HTTPException(status_code=404, detail="entity did not found")
        return entity

    async def get_entities(self, async_session: AsyncSession) -> BaseEntityModel:
        selected_entities_execution = await async_session.execute(
            select(self.entity_model)
            .order_by(self.entity_model.create_at.desc())
            .limit(DB_FETCH_LIMIT)
        )
        return selected_entities_execution.scalars().all()
