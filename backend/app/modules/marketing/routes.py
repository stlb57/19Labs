from fastapi import APIRouter, Depends, HTTPException, status
from .schemas import PublicLabProfile
from .services import ProfileService

router = APIRouter(prefix="/marketing", tags=["Public Marketing Profile"])

def get_profile_service():
    return ProfileService()

@router.get("/profile/{slug}", response_model=PublicLabProfile)
async def get_lab_profile(
    slug: str,
    service: ProfileService = Depends(get_profile_service)
):
    """
    Public Endpoint: Fetches SEO-Optimized profile data for SSG/SSR.
    No Authentication Required.
    """
    profile = service.get_profile_by_slug(slug)
    if not profile:
        raise HTTPException(status_code=404, detail="Lab not found")
    return profile
