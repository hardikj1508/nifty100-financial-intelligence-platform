"""Portfolio API endpoints."""

from fastapi import APIRouter


router = APIRouter(
    prefix="/portfolio",
    tags=["Portfolio"],
)