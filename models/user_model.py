from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from models.base_model import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(String, primary_key=True)
    name = Column(String)
    parsed_logs = relationship('ParsedLog', back_populates='user')
