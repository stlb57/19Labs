from fastapi import APIRouter, Depends, HTTPException, status
from .schemas import OTPRequest, OTPVerify, TokenResponse, PortalDashboard
from .services import PortalService

router = APIRouter(prefix="/portal", tags=["Patient Portal"])
service = PortalService()

@router.post("/generate-otp")
async def generate_otp(payload: OTPRequest):
    otp = await service.generate_otp(payload.phone)
    # Don't return OTP in real response, send via SMS
    return {"message": "OTP sent to mobile number.", "debug_otp": otp}

@router.post("/login", response_model=TokenResponse)
async def login_portal(payload: OTPVerify):
    is_valid = await service.verify_otp(payload)
    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    # Issue Mock JWT
    return {
        "access_token": f"mock_patient_token_for_{payload.phone}",
        "token_type": "bearer"
    }

@router.get("/dashboard", response_model=PortalDashboard)
async def get_dashboard(token: str = "mock_token"):
    # In real app, decode token to get user Identity
    return await service.get_dashboard("9999999999")
