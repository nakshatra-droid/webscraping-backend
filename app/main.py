import os

from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from app.api.v1.endpoints.pages import router as pages_router
from app.api.v1.routes import routers as api_v1_router
from app.config.config import Config
from app.database.database import get_db
from app.exceptions import ExceptionHandlers
from app.middleware.auth_asgi import AuthASGIMiddleware
from app.schemas.common_schemas import MessageResponse


app = FastAPI(
    title="Web Scraping Data API Service",
    description="API for managing and accessing web scraping data efficiently.",
    version="1.0.0",
)

# Setup global exception handlers
ExceptionHandlers.setup_exception_handlers(app)

# Add unified ASGI authentication middleware
app.add_middleware(AuthASGIMiddleware)

# Mount static files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount(
    "/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static"
)

# Include routers
app.include_router(api_v1_router, prefix=Config.API)
app.include_router(pages_router, prefix=Config.UI_API, tags=["ui"])


@app.get(
    path="/",
    description="Root endpoint for the Web Scraping Data API Service with health check",
    response_model=MessageResponse,
)
def health_check() -> MessageResponse:
    return MessageResponse(
        message="Web Scraping Data API Service",
        data={
            "info": "This API allows you to manage and access web scraping data efficiently.",
            "status": "running",
        },
    )


@app.get(
    path="/db-test",
    description="Test database connection",
    response_model=MessageResponse,
)
async def db_test(db=Depends(get_db)) -> MessageResponse:
    try:
        if db:
            await db.execute(text("SELECT 1"))
            return MessageResponse(
                message="Database connection successful", data={"status": "connected"}
            )
    except Exception as e:
        return MessageResponse(
            message=f"Database connection failed: {str(e)}", data={"status": "failed"}
        )
