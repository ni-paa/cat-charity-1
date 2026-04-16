from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.models.donation import Donation
from app.schemas.donation import DonationCreate, DonationDB, DonationFullInfoDB
from app.services.investment import process_investment

router = APIRouter()


@router.get('/', response_model=List[DonationFullInfoDB])
async def get_all_donations(
    session: AsyncSession = Depends(get_async_session),
):
    """Показать список всех пожертвований."""
    result_all_donations = await session.execute(
        select(Donation).order_by(Donation.create_date)
    )
    return result_all_donations.scalars().all()


@router.post('/', response_model=DonationDB)
async def create_donation(
    donation_in: DonationCreate,
    session: AsyncSession = Depends(get_async_session),
):
    """Создать пожертвование."""
    donation = Donation(
        full_amount=donation_in.full_amount,
        comment=donation_in.comment,
    )
    session.add(donation)
    await session.flush()

    # Запускаем процесс инвестирования
    await process_investment(session)

    await session.refresh(donation)
    return donation
