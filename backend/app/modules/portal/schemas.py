from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# OTP Flow
class OTPRequest(BaseModel):
    phone: str = Field(..., pattern=r"^\d{10}$")

class OTPVerify(BaseModel):
    phone: str
    otp: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

# Dashboard Data
class ResultTrend(BaseModel):
    date: str
    value: float
    flag: str

class PortalDashboard(BaseModel):
    patient_name: str
    recent_reports: List[dict] # {id, date, test_names}
    health_trends: List[ResultTrend] # Mocked for demo
