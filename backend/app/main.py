from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app.routers import ai, dashboard, employees, projects, seats

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Ethara Seat Allocation & Project Mapping System",
    description="API for managing employee seat allocation, project mapping, and AI-assisted queries",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins + ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(employees.router, prefix="/api")
app.include_router(projects.router, prefix="/api")
app.include_router(seats.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(ai.router, prefix="/api")


@app.get("/")
def root():
    return {
        "message": "Ethara Seat Allocation & Project Mapping System API",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}
