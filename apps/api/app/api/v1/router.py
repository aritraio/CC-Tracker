from fastapi import APIRouter

from app.api.v1.endpoints import analytics, anomalies, health, statements

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(statements.router)
api_router.include_router(analytics.router)
api_router.include_router(anomalies.router)
