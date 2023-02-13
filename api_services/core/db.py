import logging
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy import MetaData
from typing import List, Dict, Union
from core.singleton import MetaSingleton
from core import config_loader as config_loader
from core.constants import DB_NAMING_CONVENTION

logger = logging.getLogger(__name__)
config = config_loader.Config()


class DB(metaclass=MetaSingleton):
    def __init__(self):
        self.db_engine = self.__create_engine()
        self.metadata_obj: MetaData = MetaData(naming_convention=DB_NAMING_CONVENTION)

    def __create_engine(self) -> AsyncEngine:
        logger.error(config.get(config_loader.DB_URI))
        engine = create_async_engine(
            config.get(config_loader.DB_URI),
            echo=True,
        )
        return engine

    @staticmethod
    def row_to_dict(row) -> Union[Dict, None]:
        if row is None:
            return None
        d = {}
        for column in row.__table__.columns:
            d[column.name] = getattr(row, column.name)
        return d

    @classmethod
    def rows_to_list_of_dict(cls, rows) -> List[Dict]:
        # todo should yield ?
        return [cls.row_to_dict(row) for row in rows if row is not None]
