from pydantic import BaseModel, EmailStr
from typing import List, Optional
from uuid import UUID
from datetime import datetime

class PermissionSchema(BaseModel):
    id: UUID
    slug: str
    description: str
    module_group: str

class RoleBase(BaseModel):
    name: str
    is_system_default: bool = False

class RoleRead(RoleBase):
    id: UUID
    lab_id: Optional[UUID]
    permissions: List[PermissionSchema] = []

class RoleUpdate(BaseModel):
    permission_ids: List[UUID]

class StaffInviteRequest(BaseModel):
    email: EmailStr
    role_id: UUID
    full_name: str

class StaffInviteRead(BaseModel):
    id: UUID
    email: str
    role_name: str
    status: str # pending, accepted, expired
    expires_at: datetime
    invite_link: Optional[str] = None # Only returned on creation for debugging/demo

class UserUpdate(BaseModel):
    is_active: bool
    role_id: Optional[UUID]
