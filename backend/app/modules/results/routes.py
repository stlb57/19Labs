from fastapi import APIRouter, Depends, HTTPException
from typing import List
from uuid import UUID
from .schemas import ResultBatchUpdate, ResultRead
from .services import ResultService

router = APIRouter(prefix="/results", tags=["Result Engine"])

def get_service():
    return ResultService()

@router.post("/batch", response_model=List[ResultRead])
async def save_result_batch(
    payload: ResultBatchUpdate,
    service: ResultService = Depends(get_service)
):
    """
    Zero-Mouse Entry Endpoint.
    Accepts a batch of results, applies formulas, saves to draft/commit.
    """
    return await service.save_batch(payload)

@router.get("/{accession_id}", response_model=List[ResultRead])
async def get_accession_results(
    accession_id: UUID,
    service: ResultService = Depends(get_service)
):
    return await service.get_results_by_accession(accession_id)
