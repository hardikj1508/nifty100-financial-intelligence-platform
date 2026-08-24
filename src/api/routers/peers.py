"""Peer comparison API endpoints."""

from fastapi import APIRouter


router = APIRouter(
    prefix="/peers",
    tags=["Peers"],
)