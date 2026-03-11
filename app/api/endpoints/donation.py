from typing import Annotated

from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.donation import donation_crud
from app.core.db import get_async_session
from app.core.user import current_superuser, current_user
from app.models import User
from app.services.investment import invest
from app.schemas.donation import DonationFullInfoDB, DonationCreate, DonationDB

router = APIRouter()

SessionDep = Annotated[AsyncSession, Depends(get_async_session)]


@router.get(
    "/", response_model=list[DonationFullInfoDB],
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)]
)
async def get_all_donations(
        session: SessionDep
):
    """
    Показать список всех пожертвований.

    Только для суперюзеров.
    """
    donations = await donation_crud.get_multi(session=session)
    return donations


@router.post(
    "/", response_model=DonationDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_user)]
)
async def create_donation(
        donation: DonationCreate,
        session: SessionDep,
        user: User = Depends(current_user),
):
    """
    Сделать пожертвование.

    Только для зарегистрированных пользователей.
    """
    donation = await donation_crud.create(
        session=session, obj_in=donation, user=user
    )
    donation = await invest(session, donation)
    return donation


@router.get(
    "/my", response_model=list[DonationDB],
    response_model_exclude_none=True,
    dependencies=[Depends(current_user)]
)
async def get_user_donations(
        session: SessionDep,
        user: User = Depends(current_user)
):
    """
    Показать список пожертвований пользователя, выполняющего запрос.

    Только для зарегистрированных пользователей.
    """
    donation = await donation_crud.get_by_user(
        session=session, user=user
    )
    return donation
