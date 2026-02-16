from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.api import api_router
from app.core.config import settings
from app.core.database import engine, Base
from app.core.security import get_password_hash
from app.models import specialization, user
from sqlalchemy import select
from app.core.database import SessionLocal

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with SessionLocal() as db:
        # Seed Specializations
        specs = ["General Medicine", "Cardiology", "Orthopedics", "Pediatrics", "Neurology", "Oncology"]
        for spec_name in specs:
            result = await db.execute(select(specialization.Specialization).filter(specialization.Specialization.name == spec_name))
            if not result.scalars().first():
                db.add(specialization.Specialization(name=spec_name))
        
        # Seed Superuser
        result = await db.execute(select(user.User).filter(user.User.email == settings.FIRST_SUPERUSER))
        if not result.scalars().first():
            superuser = user.User(
                email=settings.FIRST_SUPERUSER,
                hashed_password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
                full_name="Super Admin",
                role=user.UserRole.SUPER_ADMIN.value,
                is_active=True,
                is_verified=True
            )
            db.add(superuser)
        
        await db.commit()
    
    yield
    # Shutdown
    # await engine.dispose()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

from starlette.middleware.sessions import SessionMiddleware

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.add_middleware(SessionMiddleware, secret_key=settings.SESSION_SECRET)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "Welcome to Life Health CRM API"}
