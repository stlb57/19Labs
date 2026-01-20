from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.modules.onboarding.routes import router as onboarding_router

app = FastAPI(
    title="19 Labs API",
    description="High-Performance Clinical SaaS API",
    version="1.0.0"
)

# CORS Configuration
origins = [
    "http://localhost:3000", # Next.js Frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Module Routers
from app.modules.iam.routes import router as iam_router
from app.modules.auth.routes import router as auth_router
from app.modules.marketing.routes import router as marketing_router
from app.modules.billing.routes import router as billing_router

app.include_router(onboarding_router)
app.include_router(iam_router)
app.include_router(auth_router)
app.include_router(marketing_router)
app.include_router(billing_router)

@app.get("/")
async def health_check():
    return {"status": "ok", "service": "19 Labs Core"}
