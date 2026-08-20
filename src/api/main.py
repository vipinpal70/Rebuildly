from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.chatbot import router as chatbot_router
from src.api.admin import router as admin_router
from src.api.crm import router as crm_router
from src.storage import init_db
from src.security import seed_admin_user

app = FastAPI(
    title="Opportunity Finder & Web Modernization API",
    description="Backend API for Lead Discovery, Technical Auditing, AI Receptionist & Outreach Pipeline.",
    version="1.0.0"
)

# Enable CORS for Next.js Client Template
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chatbot_router)
app.include_router(admin_router)
app.include_router(crm_router)


@app.on_event("startup")
async def on_startup():
    await init_db()
    await seed_admin_user()


@app.get("/")
async def root():
    return {
        "system": "Opportunity Finder API Engine",
        "status": "online",
        "docs": "/docs"
    }
