from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID

# Import schemas and services
from .schemas import (
    LabOnboardingInit, 
    GooglePlaceResult, 
    PresignedURLRequest, 
    PresignedURLResponse
)
from .services import OnboardingService

router = APIRouter(prefix="/onboarding", tags=["Onboarding"])

# Dependency Injection for Service (Mock DB session for now)
def get_onboarding_service():
    # In production: db = SessionLocal(); try: yield OnboardingService(db); finally: db.close()
    return OnboardingService(db_session=None)

@router.post("/init", status_code=status.HTTP_201_CREATED)
async def init_lab_onboarding(data: LabOnboardingInit, service: OnboardingService = Depends(get_onboarding_service)):
    """
    Step 1: Initialize Lab Identity.
    """
    # Logic: Insert into 'labs' table
    return {"message": "Lab initialized", "lab_id": "mock-uuid-1234", "satus": "pending_setup"}

@router.get("/google-places/{place_id}", response_model=GooglePlaceResult)
async def get_google_place_details(place_id: str, service: OnboardingService = Depends(get_onboarding_service)):
    """
    Fetch details from Google Places (via Service wrapper).
    """
    return await service.fetch_google_place_details(place_id)

@router.post("/presigned-url", response_model=PresignedURLResponse)
async def get_presigned_url(
    payload: PresignedURLRequest, 
    lab_id: UUID, # In real app, get this from JWT Auth
    service: OnboardingService = Depends(get_onboarding_service)
):
    """
    Generate secure S3 upload URL for docs.
    """
    try:
        return await service.generate_presigned_url(lab_id, payload.filename, payload.content_type, payload.content_md5)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/bundle-suggestion")
async def check_bundle_suggestion(test_ids: List[UUID], service: OnboardingService = Depends(get_onboarding_service)):
    """
    Step 3: Check for Bundling Opportunities (Association Rule Mining).
    """
    suggestion = await service.calculate_bundling_suggestion(test_ids)
    if not suggestion:
        return {"has_suggestion": False}
    return {"has_suggestion": True, "suggestion": suggestion}
