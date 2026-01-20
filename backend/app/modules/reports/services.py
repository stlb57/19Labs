from uuid import UUID, uuid4
from typing import List
from datetime import datetime
from .schemas import ReviewQueueItem, AuthorizationRequest

# Mock Data
MOCK_QUEUE = [
    ReviewQueueItem(
        booking_id=uuid4(), accession_id=uuid4(),
        patient_name="Amit Patel", patient_age=52, patient_gender="M",
        test_names=["Troponin I", "CK-MB"],
        critical_count=1, status="pending_review", is_stat=True
    ),
    ReviewQueueItem(
        booking_id=uuid4(), accession_id=uuid4(),
        patient_name="Sneha Gupta", patient_age=28, patient_gender="F",
        test_names=["CBC"],
        critical_count=0, status="pending_review", is_stat=False
    )
]

class ReviewService:
    async def get_pending_reviews(self) -> List[ReviewQueueItem]:
        # Sort by STAT then Critical Count
        return sorted(MOCK_QUEUE, key=lambda x: (not x.is_stat, -x.critical_count))

class AuthorizationService:
    async def authorize_report(self, payload: AuthorizationRequest, user_id: UUID):
        # 1. Verify User is Doctor/Pathologist
        # 2. Lock Booking
        # 3. Stamp Signature
        
        # Mock Logic: Remove from queue
        global MOCK_QUEUE
        MOCK_QUEUE = [q for q in MOCK_QUEUE if q.booking_id != payload.booking_id]
        
        return {"status": "authorized", "timestamp": datetime.now(), "signed_by": user_id}

class AmendmentService:
    async def amend_result(self, result_id: UUID, new_value: str, reason: str, user_id: UUID):
        # 1. Log old value to result_amendments
        # 2. Update test_results
        return {"status": "amended", "reason": reason}
