from __future__ import annotations
from datetime import datetime
import uuid
from sqlalchemy import Column, Integer, DateTime, String
from models.base_model import Base


class RawLog(Base):
    __tablename__ = 'raw_logs'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    create_time = Column(DateTime, index=True, default=datetime.utcnow)
    run_time = Column(DateTime, index=True)
    content = Column(String)
    log_file_path = Column(String)
    line_number = Column(Integer)
    hash_id = Column(String, unique=True, nullable=False, index=True)

    def __eq__(self, other: [RawLog, None]):
        return self.hash_id == getattr(other, 'hash_id', None)
