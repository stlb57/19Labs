from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime

class ReviewQueueItem(BaseModel):
    booking_id: UUID
    accession_id: UUID
    patient_name: str
    patient_age: int
    patient_gender: str
    test_names: List[str]
    critical_count: int # Number of panic values
    status: str
    is_stat: bool

class AuthorizationRequest(BaseModel):
    booking_id: UUID
    # Signature is inferred from logged-in user

class AmendmentRequest(BaseModel):
    result_id: UUID
    new_value: str
    reason: str
