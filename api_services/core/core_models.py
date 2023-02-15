from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy import Column, DateTime, func


class BaseEntityModel(object):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    create_at = Column(DateTime, server_default=func.now())
    update_at = Column(DateTime, server_default=func.now())
