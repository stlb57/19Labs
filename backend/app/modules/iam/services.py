import secrets
import hashlib
from datetime import datetime, timedelta
from uuid import UUID
from typing import Optional
# In production, import DB models/session

class StaffService:
    def __init__(self, db_session, current_lab_id: UUID):
        self.db = db_session
        self.lab_id = current_lab_id

    async def check_staff_quota(self) -> bool:
        """
        Check if lab has reached its staff limit.
        Query: SELECT count(*) FROM users WHERE lab_id = :id ...
        """
        # Mock Logic: Check 'labs' table for staff_limit vs (users count + pending invites)
        # Assuming limit is 5 for now
        current_count = 2 
        limit = 5
        return current_count < limit

    async def create_invite(self, email: str, role_id: UUID) -> str:
        """
        Generates a secure token, hashes it for DB, returns raw token for email.
        """
        if not await self.check_staff_quota():
            raise ValueError("Staff quota exceeded. Upgrade plan to add more seats.")

        # 1. Generate High-Entropy Token
        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        
        expires_at = datetime.utcnow() + timedelta(hours=48)

        # 2. Store in DB (Mock)
        # INSERT INTO staff_invites (lab_id, email, token_hash, role_id, expires_at) VALUES (...)
        print(f"DB INSERT: Invite for {email} with hash {token_hash} expires {expires_at}")

        # 3. Return generic link (Simulating "Click here" email)
        return f"http://localhost:3000/auth/accept-invite?token={raw_token}"

    async def get_roles_with_permissions(self):
        """
        Fetch all roles available to this lab (System Defaults + Custom Lab Roles).
        """
        # Mock Data Structure simulating a joined query response
        return [
            {
                "id": "uuid-admin", "name": "Admin", "is_system_default": True, 
                "permissions": [{"slug": "staff:invite"}, {"slug": "lab:manage"}]
            },
            {
                "id": "uuid-tech", "name": "Technician", "is_system_default": True, 
                "permissions": [{"slug": "results:enter"}]
            }
        ]
