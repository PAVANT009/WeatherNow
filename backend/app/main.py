"""WeatherNow FastAPI entrypoint.

Stage 3 wires CORS, the ``/api/v1`` router, and structured ``AppError`` handling.
Weather fetch and exercise endpoints arrive in later stages.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.config import get_settings
from app.core.exceptions import AppError

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="District-Based Live Weather Comparison Platform",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_prefix)


@app.exception_handler(AppError)
async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
    """Map domain errors to ``{"detail": {"code", "message"}}`` JSON."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.to_detail()},
    )


@app.get("/")
def root() -> dict[str, str]:
    """Root endpoint – confirms the API process is running."""
    return {
        "message": "WeatherNow API is running",
        "docs": "/docs",
        "health": f"{settings.api_prefix}/health",
    }
