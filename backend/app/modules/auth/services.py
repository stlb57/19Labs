from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from passlib.context import CryptContext
from uuid import uuid4, UUID
from .schemas import OwnerSignupRequest, TokenPayload

# --- Configuration ---
# In production, load from env
SECRET_KEY = "change_this_to_a_secure_random_string_in_production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

# --- Password Hashing ---
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

class AuthService:
    def verify_password(self, plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password):
        return pwd_context.hash(password)

    def create_tokens(self, user_id: UUID, lab_id: UUID, role_slug: str):
        # 1. Access Token
        access_payload = {
            "sub": str(user_id),
            "lab_id": str(lab_id),
            "role": role_slug,
            "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        }
        access_token = jwt.encode(access_payload, SECRET_KEY, algorithm=ALGORITHM)

        # 2. Refresh Token
        refresh_token_plain = str(uuid4()) # In real app, this is randomized string
        refresh_token_exp = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        # Store refresh_token_hash in DB here (omitted for mock)
        
        return {
            "access_token": access_token, 
            "refresh_token": refresh_token_plain,
            "token_type": "bearer"
        }

    async def signup_owner(self, payload: OwnerSignupRequest):
        """
        Atomic Transaction: Create Lab -> Create User -> Seed Defaults
        """
        # Mocking DB Transaction
        print("START TRANSACTION")
        
        # 1. Create Lab
        lab_id = uuid4()
        print(f"INSERT INTO labs (id, name) VALUES ('{lab_id}', '{payload.lab_name}')")

        # 2. Key Role Setup (Admin)
        role_id = uuid4() 
        # In real code, fetch System Default 'Admin' role ID or create one
        
        # 3. Create User
        user_id = uuid4()
        hashed_pw = self.get_password_hash(payload.password)
        print(f"INSERT INTO users (id, email, password_hash, lab_id) VALUES ('{user_id}', '{payload.email}', '***', '{lab_id}')")
        
        print("COMMIT TRANSACTION")
        
        # Auto-Login
        return self.create_tokens(user_id, lab_id, "admin")

    async def accept_invite(self, token: str, new_password: str):
        # 1. Verify Token Hash in DB
        # 2. If valid and not expired:
        #    Update User -> password_hash = hash(new_password), is_active=True
        #    Update Invite -> status='accepted'
        #    Return Tokens
        return {"status": "success", "msg": "Password set. You can now login."}
