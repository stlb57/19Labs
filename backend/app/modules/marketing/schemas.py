from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID

class Badge(BaseModel):
    id: str
    label: str
    icon: str # Lucide icon name, e.g., 'Award', 'Zap'
    color: str # Tailwind class, e.g., 'text-green-600'
    description: str

class PublicCatalogItem(BaseModel):
    test_name: str
    description: str
    tat_hours: int
    price: float
    is_home_collection: bool
    department: str
    badges: List[Badge] = []

class PublicLabProfile(BaseModel):
    id: UUID
    name: str
    slug: str
    description: str
    address: str
    city: str
    rating: float
    review_count: int
    logo_url: Optional[str]
    contact_phone: str
    
    # Marketing Metrics
    badges: List[Badge] = []
    catalog: List[PublicCatalogItem] = []
