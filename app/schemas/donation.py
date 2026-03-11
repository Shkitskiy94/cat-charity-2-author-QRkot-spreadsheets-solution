import datetime as dt
from typing import Optional

from pydantic import BaseModel, PositiveInt, ConfigDict


class DonationBase(BaseModel):
    full_amount: PositiveInt
    comment: Optional[str] = None

    model_config = ConfigDict(extra="forbid", str_min_length=1)


class DonationCreate(DonationBase):
    pass


class DonationDB(DonationBase):
    id: int
    create_date: dt.datetime

    model_config = ConfigDict(from_attributes=True)


class DonationFullInfoDB(DonationDB):
    user_id: int
    invested_amount: int
    fully_invested: bool
    close_date: Optional[dt.datetime] = None
