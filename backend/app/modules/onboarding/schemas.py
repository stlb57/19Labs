from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List
from uuid import UUID

class LabOnboardingInit(BaseModel):
    lab_name: str
    owner_name: str
    phone: str
    address: str
    google_place_id: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None

class LabProfileUpdate(BaseModel):
    whatsapp_phone: Optional[str] = None
    license_no: Optional[str] = None
    staff_limit: Optional[int] = None
    description: Optional[str] = None
    is_nabl_accredited: bool = False

class GooglePlaceResult(BaseModel):
    place_id: str
    name: str
    address: str
    phone: Optional[str] = None
    lat: float
    lng: float
    rating: Optional[float] = None

class PresignedURLRequest(BaseModel):
    filename: str
    content_type: str
    content_md5: str  # Checksum integrity

class PresignedURLResponse(BaseModel):
    url: str
    s3_key: str
    expires_in: int = 60

class LabCatalogItem(BaseModel):
    test_id: UUID
    price: float
    tat_mins: int
    instructions: Optional[str] = None

class PriceIntelligenceResponse(BaseModel):
    test_id: UUID
    regional_avg_price: float
    nearby_competitors_count: int
    is_gap_opportunity: bool # True if <10% labs offer this

class OnboardingStatusObject(BaseModel):
    step: int
    completion_percentage: int
    missing_fields: List[str]
