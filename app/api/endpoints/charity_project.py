from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.models.charity_project import CharityProject
from app.schemas.charity_project import (
    CharityProjectCreate,
    CharityProjectDB,
    CharityProjectUpdate,
)
from app.services.investment import process_investment

router = APIRouter()


@router.get('/', response_model=List[CharityProjectDB])
async def get_all_charity_projects(
    session: AsyncSession = Depends(get_async_session),
):
    """Показать список всех целевых проектов."""
    result = await session.execute(
        select(CharityProject).order_by(CharityProject.create_date)
    )
    return result.scalars().all()


@router.post('/', response_model=CharityProjectDB)
async def create_charity_project(
    project_in: CharityProjectCreate,
    session: AsyncSession = Depends(get_async_session),
):
    """Создать целевой проект."""
    # Проверка на уникальность имени
    result = await session.execute(
        select(CharityProject).where(CharityProject.name == project_in.name)
    )
    if result.scalars().first():
        raise HTTPException(
            status_code=400,
            detail='Проект с таким именем уже существует!',
        )

    project = CharityProject(
        name=project_in.name,
        description=project_in.description,
        full_amount=project_in.full_amount,
    )
    session.add(project)
    await session.flush()

    # Запускаем процесс инвестирования
    await process_investment(session)

    # Обновляем объект проекта из БД
    await session.refresh(project)
    return project


@router.patch('/{project_id}', response_model=CharityProjectDB)
async def update_charity_project(
    project_id: int,
    project_in: CharityProjectUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    """Редактировать целевой проект."""
    project = await session.get(CharityProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail='Проект не найден')

    if project.fully_invested:
        raise HTTPException(
            status_code=400,
            detail='Закрытый проект нельзя редактировать!',
        )

    # Проверка на уникальность имени
    if project_in.name is not None and project_in.name != project.name:
        result = await session.execute(
            select(CharityProject).where(
                CharityProject.name == project_in.name,
                CharityProject.id != project_id,
            )
        )
        if result.scalars().first():
            raise HTTPException(
                status_code=400,
                detail='Проект с таким именем уже существует!',
            )

    # Проверка full_amount >= invested_amount
    if (
        project_in.full_amount is not None
        and project_in.full_amount < project.invested_amount
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                'Нелья установить значение full_amount '
                'меньше уже вложенной суммы.'
            ),
        )

    # Обновляем поля
    if project_in.name is not None:
        project.name = project_in.name
    if project_in.description is not None:
        project.description = project_in.description
    if project_in.full_amount is not None:
        project.full_amount = project_in.full_amount
        # Если после изменения full_amount проект становится закрытым
        if project.invested_amount >= project.full_amount:
            project.fully_invested = True
            project.close_date = datetime.now()

    session.add(project)
    await session.commit()
    await session.refresh(project)
    return project


@router.delete('/{project_id}', response_model=CharityProjectDB)
async def delete_charity_project(
    project_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Удалить целевой проект."""
    project = await session.get(CharityProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail='Проект не найден')

    if project.invested_amount > 0:
        raise HTTPException(
            status_code=400,
            detail=(
                'В проект были внесены средства, не подлежит удалению!'
            ),
        )

    await session.delete(project)
    await session.commit()
    return project
