from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.yandex_client import get_yandex_client, YandexDiskClient
from app.core.user import current_superuser
from app.crud.charity_project import charity_project_crud
from app.services.yandex_api import create_simple_report

router = APIRouter()


@router.post(
    '/',
    response_model=str,
    dependencies=[Depends(current_superuser)],
    summary="Создать Excel отчёт на Яндекс.Диске",
    description="""
    Создаёт Excel файл с отчётом по закрытым проектам, 
    отсортированным по скорости сбора средств.

    Файл сохраняется на Яндекс.Диске в папке "QRKot Reports"
    и становится доступным по публичной ссылке.

    Требуются права суперпользователя.
    """
)
async def create_yandex_report(
        session: AsyncSession = Depends(get_async_session),
        yandex_client: YandexDiskClient = Depends(get_yandex_client)
) -> str:
    """
    Создание Excel отчёта на Яндекс.Диске
    """
    # Получаем проекты из БД (уже отсортированные по времени сбора)
    projects = await charity_project_crud.get_projects_by_completion_rate(session)

    if not projects:
        raise HTTPException(
            status_code=404,
            detail="Нет закрытых проектов для формирования отчёта"
        )

    try:
        # Создаём отчёт и получаем ссылку
        file_url = await create_simple_report(yandex_client, projects)
        return file_url
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при создании отчёта: {str(e)}"
        )
