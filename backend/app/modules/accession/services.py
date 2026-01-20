from uuid import UUID, uuid4
from typing import List
from datetime import datetime
from .schemas import AccessionRead, AccessionStartRequest

# Mock Data
MOCK_ACCESSIONS = []

class AccessionService:
    async def split_booking(self, booking_id: UUID) -> List[AccessionRead]:
        """
        MOCK Logic: In a real system, we'd query Master Test metadata.
        Here, we'll just deterministically create 2 tubes for any booking.
        """
        existing = [a for a in MOCK_ACCESSIONS if a.booking_id == booking_id]
        if existing:
            return existing

        # Create Mock Accessions
        # Tube 1: EDTA (Purple)
        acc1 = AccessionRead(
            id=uuid4(),
            booking_id=booking_id,
            accession_number=f"LAB-{datetime.now().year}-001-A",
            container_type="EDTA (Lavender)",
            status="pending",
            test_names=["CBC", "HbA1c"]
        )
        
        # Tube 2: Serum (Yellow/Red)
        acc2 = AccessionRead(
            id=uuid4(),
            booking_id=booking_id,
            accession_number=f"LAB-{datetime.now().year}-001-B",
            container_type="Serum (Yellow)",
            status="pending",
            test_names=["Thyroid Profile", "Vitamin D"]
        )
        
        MOCK_ACCESSIONS.extend([acc1, acc2])
        return [acc1, acc2]

    async def get_pending_worklist(self) -> List[AccessionRead]:
        return [a for a in MOCK_ACCESSIONS if a.status == 'pending']

    async def mark_collected(self, accession_id: UUID) -> AccessionRead:
        acc = next((a for a in MOCK_ACCESSIONS if a.id == accession_id), None)
        if not acc:
            raise ValueError("Accession not found")
        
        acc.status = 'collected'
        acc.collected_at = datetime.now()
        return acc

    async def receive_at_lab(self, accession_id: UUID) -> AccessionRead:
        acc = next((a for a in MOCK_ACCESSIONS if a.id == accession_id), None)
        if not acc:
             raise ValueError("Accession not found")
             
        acc.status = 'received'
        acc.received_at = datetime.now()
        return acc
