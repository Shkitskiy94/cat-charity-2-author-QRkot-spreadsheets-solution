import datetime as dt
from typing import Union

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import CharityProject, Donation

FinancialClass = Union[CharityProject, Donation]


async def invest(session: AsyncSession, new_obj: FinancialClass):
    new_obj_model = type(new_obj)
    if new_obj_model == Donation:
        model_to_invest = CharityProject
    else:
        model_to_invest = Donation

    objs_to_invest = await session.execute(
        select(model_to_invest).where(
            model_to_invest.fully_invested.is_(False)
        ).order_by(model_to_invest.create_date)
    )

    now = dt.datetime.now()

    target: FinancialClass
    for target in objs_to_invest.scalars().all():
        for_target_close = target.full_amount - target.invested_amount
        for_new_obj_close = new_obj.full_amount - new_obj.invested_amount

        if for_target_close <= for_new_obj_close:
            invested_batch = for_target_close
            target.fully_invested = True
            target.close_date = now
        else:
            invested_batch = for_new_obj_close

        target.invested_amount += invested_batch
        session.add(target)

        new_obj.invested_amount += invested_batch
        if new_obj.full_amount == new_obj.invested_amount:
            new_obj.fully_invested = True
            new_obj.close_date = now
            break

    session.add(new_obj)
    await session.commit()
    return new_obj
