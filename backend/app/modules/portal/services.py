from typing import Dict
from .schemas import OTPRequest, OTPVerify, PortalDashboard, ResultTrend

# Mock Stores
OTP_STORE: Dict[str, str] = {} # phone -> otp

class PortalService:
    async def generate_otp(self, phone: str) -> str:
        """
        In production, integrate Twilio/SNS.
        Here, we return a fixed mock OTP '123456'.
        """
        otp = "123456"
        OTP_STORE[phone] = otp
        print(f"DEBUG: OTP for {phone} is {otp}")
        return otp

    async def verify_otp(self, payload: OTPVerify) -> bool:
        stored = OTP_STORE.get(payload.phone)
        return stored == payload.otp

    async def get_dashboard(self, phone: str) -> PortalDashboard:
        return PortalDashboard(
            patient_name="Rajesh Kumar",
            recent_reports=[
                {"id": "rep_101", "date": "2024-03-20", "test_names": "Lipid Profile"},
                {"id": "rep_102", "date": "2023-12-15", "test_names": "CBC, HbA1c"}
            ],
            health_trends=[
                ResultTrend(date="2023-10-01", value=14.2, flag="normal"),
                ResultTrend(date="2023-11-15", value=13.8, flag="normal"),
                ResultTrend(date="2023-12-15", value=13.5, flag="low"),
                ResultTrend(date="2024-03-20", value=11.2, flag="low"),
            ]
        )

class PDFService:
    """
    Mock PDF Generation.
    In real app, use WeasyPrint/Playwright + Jinja2 Template.
    """
    async def generate_mock_pdf_url(self, report_id: str):
        return f"https://s3.aws.com/19labs/reports/{report_id}.pdf"
