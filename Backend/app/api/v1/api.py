from fastapi import APIRouter

from app.api.v1.endpoints import services, proxy, payments, analytics, alith

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(services.router, prefix="/services", tags=["services"])
api_router.include_router(proxy.router, prefix="/proxy", tags=["proxy"])
api_router.include_router(payments.router, prefix="/payments", tags=["payments"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(alith.router, prefix="/alith", tags=["alith"])