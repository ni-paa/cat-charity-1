from sqlalchemy import Column, Text

from app.models.base import CharityBase


class Donation(CharityBase):
    __tablename__ = 'donation'

    comment = Column(Text, nullable=True)
