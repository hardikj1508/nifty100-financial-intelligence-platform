"""Document API endpoints."""

from fastapi import APIRouter


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)