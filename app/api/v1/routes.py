from fastapi import APIRouter

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.users import router as user_router
from app.api.v1.endpoints.activity_logs import router as activity_logs_router
from app.api.v1.endpoints.products import (
    router as products_router,
    admin_router as products_admin_router,
)
from app.api.v1.endpoints.scraping_metadata import router as scraping_metadata_router
from app.api.v1.endpoints.embeddings import router as embeddings_router
from app.api.v1.endpoints.chat import router as chat_router
from app.api.v1.endpoints.dashboard import router as dashboard_router
from app.config.config import Config

routers = APIRouter()

routers.include_router(auth_router, prefix=Config.V1_API + "/auth", tags=["auth"])
routers.include_router(user_router, prefix=Config.V1_API + "/users", tags=["users"])
routers.include_router(
    products_router, prefix=Config.V1_API + "/products", tags=["products"]
)
routers.include_router(
    products_admin_router,
    prefix=Config.V1_API + "/admin/products",
    tags=["admin-products"],
)
routers.include_router(
    activity_logs_router,
    prefix=Config.V1_API + "/admin/activity-logs",
    tags=["admin-activity-logs"],
)
routers.include_router(
    scraping_metadata_router,
    prefix=Config.V1_API + "/admin/scraper-runs",
    tags=["admin-scraper-runs"],
)
routers.include_router(
    embeddings_router,
    prefix=Config.V1_API + "/admin/embeddings",
    tags=["admin-embeddings"],
)
routers.include_router(
    chat_router,
    prefix=Config.V1_API + "/ws",
    tags=["chat"],
)
routers.include_router(
    dashboard_router,
    prefix=Config.V1_API + "/admin",
    tags=["admin-dashboard"],
)
