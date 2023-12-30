import uuid
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from models.base_model import Base


class ParsedLog(Base):
    __tablename__ = 'parsed_logs'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    create_time = Column(DateTime, index=True)
    command_type = Column(String, index=True)
    rule_name = Column(String, index=True)
    user_id = Column(String, ForeignKey('users.id'), index=True)
    user = relationship('User', back_populates='parsed_logs')
    folder = Column(String, index=True)
    data = Column(JSON)
