from sqlalchemy import insert, update, Executable
from core.singleton import MetaSingleton
from fastapi import HTTPException
from typing_extensions import TypedDict
from models import BaseEntityModel
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from asyncpg.exceptions import UniqueViolationError, NotNullViolationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
import logging

logger = logging.getLogger(__name__)


class InsertResponse(TypedDict):
    id: UUID4


DB_FETCH_LIMIT = 50


class ApiService(metaclass=MetaSingleton):
    def __init__(self, entity_model: BaseEntityModel):
        self.entity_model: BaseEntityModel = entity_model

    async def execute(self, async_session: AsyncSession, exec_func: Executable):
        try:
            exec_res = await async_session.execute(exec_func)
        except IntegrityError as e:
            error_type = str(e.orig).split(":")[0]
            if error_type == str(UniqueViolationError):
                raise HTTPException(status_code=409, detail=str(e.orig))
            elif error_type == str(NotNullViolationError):
                raise HTTPException(status_code=409, detail=str(e.orig))
            logger.error(str(e))
        return exec_res

    async def insert_entity(
        self, async_session: AsyncSession, **values
    ) -> InsertResponse:
        logger.info(f"Try to Create Entity {values}")
        entity = await self.execute(
            async_session, insert(self.entity_model).values(**values)
        )
        # Basic entity id is last field
        return InsertResponse(id=entity.inserted_primary_key[-1])

    async def update_entity(
        self,
        async_session: AsyncSession,
        entity_id: UUID4,
        allow_change_id=False,
        **values,
    ):
        logger.info(f"Try to Update Entity {values}")
        if allow_change_id is False and "id" in values:
            del values["id"]
        update_result = await self.execute(
            async_session,
            update(self.entity_model)
            .where(self.entity_model.id == entity_id)
            .values(**values),
        )
        row_counts = update_result.rowcount
        if row_counts == 0:
            ApiService.raise_not_found_exception(entity_id)
        if row_counts > 1:
            raise HTTPException(status_code=500, detail="Update more than one row !!")
        return InsertResponse(id=entity_id)

    async def get_entity_by_id(
        self, async_session: AsyncSession, entity_id: UUID4
    ) -> BaseEntityModel:
        selected_entity_execution = await self.execute(
            async_session,
            select(self.entity_model).filter(self.entity_model.id == entity_id),
        )
        entity = selected_entity_execution.scalars().first()
        if not entity:
            ApiService.raise_not_found_exception(entity_id)
        return entity

    async def get_entities(self, async_session: AsyncSession) -> BaseEntityModel:
        selected_entities_execution = await self.execute(
            async_session,
            select(self.entity_model)
            .order_by(self.entity_model.create_at.desc())
            .limit(DB_FETCH_LIMIT),
        )
        return selected_entities_execution.scalars().all()

    @staticmethod
    def raise_not_found_exception(entity_id: UUID4):
        logger.info(f"entity did not found: {entity_id}")
        raise HTTPException(status_code=404, detail="entity did not found")
