from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID

from .schemas import StaffInviteRequest, RoleRead
from .services import StaffService
from .dependencies import RequirePermission

router = APIRouter(prefix="/iam", tags=["IAM & Staff"])

# Dependency Injection
def get_staff_service():
    # In production: extract lab_id from JWT
    mock_lab_id = UUID("00000000-0000-0000-0000-000000000000")
    return StaffService(db_session=None, current_lab_id=mock_lab_id)

@router.post("/staff/invite", dependencies=[Depends(RequirePermission("staff:invite"))])
async def invite_staff(
    payload: StaffInviteRequest,
    service: StaffService = Depends(get_staff_service)
):
    """
    Invite a new staff member. Protected by 'staff:invite' atomic permission.
    """
    try:
        invite_link = await service.create_invite(payload.email, payload.role_id)
        # In a real app, this link is emailed. For demo, we return it.
        return {"status": "invited", "debug_link": invite_link}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/roles", response_model=List[RoleRead], dependencies=[Depends(RequirePermission("lab:manage"))])
async def list_roles(service: StaffService = Depends(get_staff_service)):
    """
    List all roles (System + Lab Specific) for the Permissions Matrix.
    """
    return await service.get_roles_with_permissions()
