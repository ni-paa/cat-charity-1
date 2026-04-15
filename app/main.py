from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.project_name,
    description='Благотворительный фонд поддержки котиков QRKot',
)

app.include_router(api_router)


@app.get('/')
async def root():
    return {'message': 'QRKot API is running'}
