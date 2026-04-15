from datetime import datetime
from typing import Optional

from pydantic import BaseModel, PositiveInt


class DonationCreate(BaseModel):
    full_amount: PositiveInt
    comment: Optional[str] = None

    class Config:
        extra = 'forbid'


class DonationDB(BaseModel):
    id: int
    full_amount: PositiveInt
    comment: Optional[str] = None
    create_date: datetime

    class Config:
        from_attributes = True


class DonationFullInfoDB(DonationDB):
    invested_amount: int = 0
    fully_invested: bool = False
    close_date: Optional[datetime] = None
