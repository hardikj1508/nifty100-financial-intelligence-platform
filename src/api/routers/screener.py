"""Stock screener API endpoints."""

from fastapi import APIRouter


router = APIRouter(
    prefix="/screener",
    tags=["Screener"],
)