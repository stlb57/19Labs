from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime

class PatientBase(BaseModel):
    name: str = Field(..., min_length=2)
    phone: str = Field(..., pattern=r"^\+?[1-9]\d{1,14}$") # E.164-ish
    age: int
    gender: str = Field(..., pattern="^(M|F|O)$")
    email: Optional[str] = None
    address: Optional[str] = None

class PatientCreate(PatientBase):
    pass

class PatientRead(PatientBase):
    id: UUID
    lab_id: UUID
    pid: int
    created_at: datetime

class CartItem(BaseModel):
    catalog_item_id: UUID
    price: float
    test_name: str

class BookingCreate(BaseModel):
    patient_id: Optional[UUID] = None # If existing patient
    new_patient: Optional[PatientCreate] = None # If new patient
    doctor_id: Optional[UUID] = None
    
    items: List[CartItem]
    discount_amount: float = 0.0
    payment_method: str = "cash"

class BookingRead(BaseModel):
    id: UUID
    booking_readable_id: str
    patient: PatientRead
    net_total: float
    status: str
    whatsapp_link: Optional[str] # Payload for frontend
