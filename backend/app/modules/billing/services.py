from uuid import UUID, uuid4
from typing import List, Optional
from datetime import datetime
from .schemas import PatientCreate, BookingCreate, PatientRead, BookingRead

# Mock DB Stores
MOCK_PATIENTS = []
MOCK_BOOKINGS = []

class PatientService:
    async def search_patients(self, query: str) -> List[PatientRead]:
        """
        Simulates Fuzzy Search (SQL LIKE %query%)
        """
        # In real DB: SELECT * FROM patients WHERE name ILIKE :q OR phone ILIKE :q
        results = [
            p for p in MOCK_PATIENTS 
            if query.lower() in p.name.lower() or query in p.phone
        ]
        return results

    async def get_or_create_patient(self, pid: Optional[UUID], new_data: Optional[PatientCreate]) -> PatientRead:
        if pid:
            # Fetch existing
            found = next((p for p in MOCK_PATIENTS if p.id == pid), None)
            if not found:
                 raise ValueError("Patient not found")
            return found
        
        if new_data:
            # Create new
            new_p = PatientRead(
                id=uuid4(),
                lab_id=uuid4(), # Current context
                pid=len(MOCK_PATIENTS) + 1001,
                created_at=datetime.now(),
                **new_data.dict()
            )
            MOCK_PATIENTS.append(new_p)
            return new_p
            
        raise ValueError("No patient data provided")

class BillingService:
    def calculate_totals(self, items: List, discount: float):
        subtotal = sum(item.price for item in items)
        # tax = subtotal * 0.18 # Example logic
        tax = 0 
        net = subtotal + tax - discount
        return subtotal, tax, net

class BookingService:
    def __init__(self):
        self.patient_service = PatientService()
        self.billing_service = BillingService()

    async def create_booking(self, payload: BookingCreate) -> BookingRead:
        # 1. Handle Patient
        patient = await self.patient_service.get_or_create_patient(
            payload.patient_id, payload.new_patient
        )

        # 2. Calculate Billing
        sub, tax, net = self.billing_service.calculate_totals(payload.items, payload.discount_amount)

        # 3. Create Transaction
        booking_id = uuid4()
        readable_id = f"LAB-{len(MOCK_BOOKINGS)+101}"
        
        # Save to DB (mock)
        booking = BookingRead(
            id=booking_id,
            booking_readable_id=readable_id,
            patient=patient,
            net_total=net,
            status="confirmed",
            whatsapp_link=self._generate_whatsapp_payload(patient, readable_id, net)
        )
        MOCK_BOOKINGS.append(booking)
        
        return booking

    def _generate_whatsapp_payload(self, patient, bid, amount):
        msg = f"Hello {patient.name}, your booking {bid} is confirmed. Total Amount: {amount}. You can track status here: https://19labs.com/track/{bid}"
        return f"https://wa.me/{patient.phone}?text={msg}"
