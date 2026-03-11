import datetime as dt
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (
    check_charity_project_before_edit, check_the_same_name
)
from app.crud.charity_project import charity_project_crud
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.services.investment import invest
from app.schemas.charity_project import (
    CharityProjectCreate, CharityProjectDB, CharityProjectUpdate,
    CharityProjectUpdateTimestamp
)

router = APIRouter()

SessionDep = Annotated[AsyncSession, Depends(get_async_session)]


@router.get(
    "/",
    response_model=list[CharityProjectDB],
    response_model_exclude_none=True,
)
async def get_all_charity_projects(
        session: SessionDep
):
    """Показать список всех целевых проектов."""
    charity_projects = await charity_project_crud.get_multi(session=session)
    return charity_projects


@router.post(
    '/',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def create_charity_project(
        project_in: CharityProjectCreate,
        session: SessionDep
):
    """
    Создать целевой проект.

    Только для суперюзеров.
    """
    await check_the_same_name(session, project_in.name)

    new_project = await charity_project_crud.create(
        session=session, obj_in=project_in
    )
    new_project = await invest(session, new_project)
    return new_project


@router.patch(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
    response_model_exclude_none=True,
)
async def update_charity_project(
        project_id: int,
        project_in: CharityProjectUpdate,
        session: SessionDep
):
    """
    Редактировать целевой проект.

    Только для суперюзеров.

    Закрытый проект нельзя редактировать;
    нельзя установить требуемую сумму меньше уже вложенной.
    """
    charity_project = await check_charity_project_before_edit(
        session, project_id
    )

    if charity_project.fully_invested:
        raise HTTPException(
            status_code=400,
            detail='Закрытый проект нельзя редактировать!'
        )

    if project_in.name:
        await check_the_same_name(session, project_in.name)

    if project_in.full_amount:
        if project_in.full_amount < charity_project.invested_amount:
            raise HTTPException(
                status_code=400,
                detail='Нельзя установить проекту меньшую сумму, '
                       'чем уже было инвестировано!'
            )
        elif project_in.full_amount == charity_project.invested_amount:
            project_in = CharityProjectUpdateTimestamp(
                **project_in.model_dump(exclude_unset=True),
                fully_invested=True,
                close_date=dt.datetime.now()
            )

    charity_project = await charity_project_crud.update(
        session=session,
        db_obj=charity_project,
        obj_in=project_in
    )
    return charity_project


@router.delete(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
    response_model_exclude_none=True,
)
async def delete_charity_project(
        project_id: int,
        session: SessionDep
):
    """
    Удалить целевой проект.

    Только для суперюзеров.

    Нельзя удалить проект, в который уже были инвестированы средства.
    """
    charity_project = await check_charity_project_before_edit(
        session, project_id
    )

    if charity_project.invested_amount > 0:
        raise HTTPException(
            status_code=400,
            detail='В проект были внесены средства, не подлежит удалению!'
        )

    charity_project = await charity_project_crud.remove(
        session=session, db_obj=charity_project
    )
    return charity_project
