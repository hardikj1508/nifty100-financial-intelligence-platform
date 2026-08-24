"""Sector API endpoints."""

from fastapi import APIRouter


router = APIRouter(
    prefix="/sectors",
    tags=["Sectors"],
)