from fastapi import APIRouter

from app.api.endpoints import charity_project, donation

api_router = APIRouter()
api_router.include_router(
    charity_project.router,
    prefix='/charity_project',
    tags=['charity_projects'],
)
api_router.include_router(
    donation.router,
    prefix='/donation',
    tags=['donations'],
)
