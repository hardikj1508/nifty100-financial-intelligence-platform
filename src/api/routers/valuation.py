"""Valuation API endpoints."""

from fastapi import APIRouter


router = APIRouter(
    prefix="/valuation",
    tags=["Valuation"],
)