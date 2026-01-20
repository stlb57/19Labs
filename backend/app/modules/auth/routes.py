from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from .schemas import OwnerSignupRequest, TokenResponse, LoginRequest, SetPasswordRequest
from .services import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])

def get_auth_service():
    return AuthService() # In prod, inject DB session

@router.post("/signup-owner", response_model=TokenResponse)
async def signup_owner(payload: OwnerSignupRequest, service: AuthService = Depends(get_auth_service)):
    """
    Public Endpoint: Registers a new Lab Owner + Admin User + Default Roles.
    Returns: Auto-login JWT.
    """
    try:
        return await service.signup_owner(payload)
    except Exception as e:
        # In prod, log error carefully
        raise HTTPException(status_code=400, detail="Signup failed. Email might be taken.")

@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), # Compatible with Swagger UI
    service: AuthService = Depends(get_auth_service)
):
    """
    Standard Login: Returns Access + Refresh Token.
    Rate Limit: 5 per 15 mins (Logic handled by middleware or limiter).
    """
    # Simulate DB lookup
    # user = service.authenticate_user(form_data.username, form_data.password)
    # For now, we mock successful login for testing flow
    if form_data.password == "wrong":
        raise HTTPException(status_code=401, detail="Invalid credentials")
        
    return service.create_tokens(
        user_id="mock-user-id", 
        lab_id="mock-lab-id", 
        role_slug="admin"
    )

@router.post("/accept-invite")
async def accept_invite(
    payload: SetPasswordRequest,
    service: AuthService = Depends(get_auth_service)
):
    """
    Finish staff onboarding by setting password.
    """
    return await service.accept_invite(payload.token, payload.new_password)
