from fastapi import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charity_project import charity_project_crud


async def check_charity_project_before_edit(
        session: AsyncSession, charity_project_id: int
):
    charity_project = await charity_project_crud.get(
        session=session, obj_id=charity_project_id
    )
    if not charity_project:
        raise HTTPException(status_code=404, detail='Проект не найден!')
    return charity_project


async def check_the_same_name(
        session: AsyncSession, project_name: str
):
    project_with_the_same_name = await charity_project_crud.get_by_name(
        session=session, project_name=project_name
    )
    if project_with_the_same_name:
        raise HTTPException(
            status_code=400,
            detail="Проект с таким именем уже существует!"
        )
