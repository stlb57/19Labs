from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime

class AccessionBase(BaseModel):
    booking_id: UUID
    container_type: str
    status: str

class AccessionRead(AccessionBase):
    id: UUID
    accession_number: str
    collected_at: Optional[datetime]
    received_at: Optional[datetime]
    status: str # 'pending', 'collected', 'received', 'rejected'
    test_names: List[str] = [] # Aggregated names for the label

class AccessionStartRequest(BaseModel):
    booking_id: UUID

class CollectionAction(BaseModel):
    accession_id: UUID
    phlebotomist_id: Optional[UUID] = None # Or inferred from current user
