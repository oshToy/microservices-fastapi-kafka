from sqlalchemy import Column, DateTime, func, String
import uuid
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from db import DB


Base = declarative_base(metadata=DB().metadata_obj)


class Crawler(Base):
    __tablename__ = "crawlers"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    html_url = Column(String, nullable=False)
    create_at = Column(DateTime, server_default=func.now())


# TODO ONLY DEV !!!
