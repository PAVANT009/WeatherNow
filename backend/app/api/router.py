"""Aggregate API routers mounted under the configured API prefix."""

from fastapi import APIRouter

from app.api.routes import cities, districts, exercises, health, weather

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(cities.router)
api_router.include_router(districts.router)
api_router.include_router(exercises.router)
api_router.include_router(weather.router)
