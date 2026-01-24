"""
Instruments router - GET /instruments
"""

from fastapi import APIRouter
from typing import List
from models import Instrument
from services.data_loader import get_instruments

router = APIRouter(tags=["instruments"])


@router.get("/instruments", response_model=List[Instrument])
def list_instruments():
    """Get all available instruments"""
    return get_instruments()
