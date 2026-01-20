from fastapi import APIRouter, Depends, HTTPException
from typing import List
from uuid import UUID
from .schemas import AccessionRead, AccessionStartRequest, CollectionAction
from .services import AccessionService

router = APIRouter(prefix="/accession", tags=["Sample Logistics"])

def get_service():
    return AccessionService()

@router.post("/split", response_model=List[AccessionRead])
async def split_booking_samples(
    payload: AccessionStartRequest,
    service: AccessionService = Depends(get_service)
):
    """
    Called when Reception confirms booking. 
    Splits order into labelled tubes.
    """
    return await service.split_booking(payload.booking_id)

@router.get("/pending", response_model=List[AccessionRead])
async def get_phlebotomy_worklist(
    service: AccessionService = Depends(get_service)
):
    return await service.get_pending_worklist()

@router.post("/collect", response_model=AccessionRead)
async def mark_sample_collected(
    payload: CollectionAction,
    service: AccessionService = Depends(get_service)
):
    try:
        return await service.mark_collected(payload.accession_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
