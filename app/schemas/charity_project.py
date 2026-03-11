import datetime as dt
from typing import Optional

from pydantic import BaseModel, Field, PositiveInt, ConfigDict


class CharityProjectBase(BaseModel):
    name: str = Field(..., min_length=5, max_length=100)
    description: str = Field(..., min_length=10)
    full_amount: PositiveInt

    model_config = ConfigDict(extra="forbid")


class CharityProjectCreate(CharityProjectBase):
    pass


class CharityProjectUpdate(CharityProjectBase):
    name: Optional[str] = Field(None, min_length=5, max_length=100)
    description: Optional[str] = Field(None, min_length=10)
    full_amount: Optional[PositiveInt] = None


class CharityProjectUpdateTimestamp(CharityProjectUpdate):
    close_date: dt.datetime
    fully_invested: bool


class CharityProjectDB(CharityProjectBase):
    id: int
    invested_amount: int
    fully_invested: bool
    create_date: dt.datetime
    close_date: Optional[dt.datetime] = None

    model_config = ConfigDict(from_attributes=True)
