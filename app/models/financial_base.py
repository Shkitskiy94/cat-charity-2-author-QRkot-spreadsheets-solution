from datetime import datetime

from sqlalchemy import (
    Boolean, DateTime, Integer
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class FinancialBase(Base):
    __abstract__ = True

    full_amount: Mapped[int] = mapped_column(Integer, nullable=False)
    invested_amount: Mapped[int] = mapped_column(Integer, default=0)
    fully_invested: Mapped[bool] = mapped_column(Boolean, default=False)
    # В default обязательно должна стоять метод now без вызова,
    # т.е. не default=datetime.now(), а default=datetime.now
    # Иначе в первом случае будет одно и то же время
    # с момента старта приложения.
    # Если используется server_default, то он ставит UTC время,
    # тогда и все остальные datetime поля в проекте должны заполняться
    # через utcnow.
    create_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    close_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
