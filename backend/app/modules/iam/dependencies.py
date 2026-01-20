from fastapi import Depends, HTTPException, status
from typing import List
from uuid import UUID

# Mock User Context until Auth Module is fully live
async def get_current_user_permissions():
    """
    In production, this extracts user from JWT, then queries:
    User -> Role -> RolePermissions -> Permissions
    """
    # Simulate an Admin user for now
    return ["staff:invite", "lab:manage", "onboarding:view"]

class RequirePermission:
    def __init__(self, required_permission: str):
        self.required_permission = required_permission

    async def __call__(self, user_perms: List[str] = Depends(get_current_user_permissions)):
        if self.required_permission not in user_perms:
             raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permission: {self.required_permission}"
            )
        return True
