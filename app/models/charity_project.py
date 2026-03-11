from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.financial_base import FinancialBase


class CharityProject(FinancialBase):
    name: Mapped[str] = mapped_column(
        String(length=100), unique=True, nullable=False
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)

    def __repr__(self):
        return (
            f'Проект {self.name} на сумму '
            f'{self.full_amount}'
        )
