from sqlalchemy import Column, String, Enum as sqlEnum, DateTime, func
from sqlalchemy.orm import declarative_base
from core.db import DB
from enum import Enum
from sqlalchemy.dialects.postgresql import UUID

Base = declarative_base(metadata=DB().metadata_obj)


class Status(str, Enum):
    Accepted = "Accepted"
    Running = "Running"
    Error = "Error"
    Complete = "Complete"


class CrawlerStatus(Base):
    __tablename__ = "crawlers_status"
    id = Column(UUID(as_uuid=True), primary_key=True)
    status = Column(sqlEnum(Status), nullable=False)
    file_path = Column(String, nullable=True)
    create_at = Column(DateTime, server_default=func.now())
    update_at = Column(DateTime, server_default=func.now())
