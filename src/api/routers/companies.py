"""Company API endpoints."""

from fastapi import APIRouter


router = APIRouter(
    prefix="/companies",
    tags=["Companies"],
)