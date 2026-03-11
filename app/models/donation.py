from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.financial_base import FinancialBase


class Donation(FinancialBase):
    comment: Mapped[str] = mapped_column(Text, nullable=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'))

    def __repr__(self):
        return (
            f'{self.user_id} инвестировал {self.full_amount}, '
            f'{self.invested_amount}, {self.create_date}'
        )
