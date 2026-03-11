from sqlalchemy import extract, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import CharityProject


class CRUDCharityProject(CRUDBase):

    async def get_by_name(self, session: AsyncSession, project_name: str):
        charity_project = await session.execute(
            select(CharityProject).where(
                CharityProject.name == project_name
            )
        )
        return charity_project.scalars().first()

    async def get_projects_by_completion_rate(
        self,
        session: AsyncSession,
    ) -> list[CharityProject]:
        """
        Метод который сортирует список со всеми закрытыми проектами
        по количеству времени, которое понадобилось на сбор средств,
        — от меньшего к большему.
        """
        projects = await session.execute(
            select(CharityProject).where(
                CharityProject.fully_invested
            ).order_by(
                extract('epoch', CharityProject.close_date) -
                extract('epoch', CharityProject.create_date)
            )
        )
        projects: list[CharityProject] = projects.scalars().all()

        return projects


charity_project_crud = CRUDCharityProject(CharityProject)
