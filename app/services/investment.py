from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.charity_project import CharityProject
from app.models.donation import Donation


async def process_investment(session: AsyncSession) -> None:
    """Распределяет свободные средства пожертвований по открытым проектам."""
    # Получаем все открытые проекты, отсортированные по дате создания
    projects_result = await session.execute(
        select(CharityProject)
        .where(CharityProject.fully_invested.is_(False))
        .order_by(CharityProject.create_date)
    )
    projects = projects_result.scalars().all()

    # Получаем все не полностью инвестированные пожертвования
    donations_result = await session.execute(
        select(Donation)
        .where(Donation.fully_invested.is_(False))
        .order_by(Donation.create_date)
    )
    donations = donations_result.scalars().all()

    for project in projects:
        for donation in donations:
            if donation.fully_invested:
                continue
            if project.fully_invested:
                break

            # Считаем сколько осталось инвестировать
            donation_remaining = (
                donation.full_amount - donation.invested_amount
            )
            project_remaining = project.full_amount - project.invested_amount

            # Определяем сумму инвестиции
            invest_amount = min(donation_remaining, project_remaining)

            # Обновляем проект
            project.invested_amount += invest_amount
            if project.invested_amount >= project.full_amount:
                project.fully_invested = True
                project.close_date = datetime.now()

            # Обновляем пожертвование
            donation.invested_amount += invest_amount
            if donation.invested_amount >= donation.full_amount:
                donation.fully_invested = True
                donation.close_date = datetime.now()

    await session.commit()
