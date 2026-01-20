from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from .schemas import PatientRead, BookingCreate, BookingRead
from .services import BookingService, PatientService

router = APIRouter(prefix="/billing", tags=["Billing & Reception"])

def get_services():
    return {
        "booking": BookingService(),
        "patient": PatientService()
    }

@router.get("/patients/search", response_model=List[PatientRead])
async def search_patients(
    q: str = Query(..., min_length=1),
    services = Depends(get_services)
):
    """
    Fuzzy search for patients by name or phone.
    """
    return await services["patient"].search_patients(q)

@router.post("/bookings", response_model=BookingRead)
async def create_booking(
    payload: BookingCreate,
    services = Depends(get_services)
):
    """
    Transactional Booking Creation.
    Creates Patient (if new) -> Creates Order -> Returns WhatsApp Link.
    """
    try:
        return await services["booking"].create_booking(payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
