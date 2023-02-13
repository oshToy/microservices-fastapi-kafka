from sqlalchemy import Column, DateTime, func, String
import uuid
from sqlalchemy.orm import declarative_base
from db import DB
from core.models import BaseEntityModel

Base = declarative_base(metadata=DB().metadata_obj)


class Crawler(Base, BaseEntityModel):
    __tablename__ = "crawlers"
    html_url = Column(String, nullable=False)