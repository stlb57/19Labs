from fastapi import APIRouter, Depends, HTTPException
from typing import List
from uuid import UUID
from .schemas import ReviewQueueItem, AuthorizationRequest
from .services import ReviewService, AuthorizationService

router = APIRouter(prefix="/reports", tags=["Pathologist Review"])

def get_services():
    return {
        "review": ReviewService(),
        "auth": AuthorizationService()
    }

@router.get("/queue", response_model=List[ReviewQueueItem])
async def get_review_queue(
    services = Depends(get_services)
):
    """
    Returns pending reports sorted by Urgency (Panic/STAT first).
    """
    return await services["review"].get_pending_reviews()

@router.post("/approve")
async def approve_report(
    payload: AuthorizationRequest,
    services = Depends(get_services)
):
    # In real app, user_id comes from JWT
    mock_user_id = UUID("00000000-0000-0000-0000-000000000000")
    return await services["auth"].authorize_report(payload, mock_user_id)
