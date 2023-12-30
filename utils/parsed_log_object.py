import json
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field, AliasChoices, Extra, validator
from models import User


class ExtraData(BaseModel):
    class Config:
        extra = Extra.allow


class ParsedLogObject(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    create_time: datetime
    command_type: str = Field(alias="type", default=None)
    rule_name: str = Field(alias="key", default=None)
    user_id: str = Field(alias="uid", default=None)
    user: Optional[User] = None
    folder: str = Field(alias="cwd", default=None)
    data: Optional[ExtraData]

    @validator("rule_name")
    def parse_rule_name(cls, v: Any) -> str:
        try:
            return json.loads(v)
        except (json.JSONDecodeError, Exception):
            return str(v)
