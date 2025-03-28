from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import router as api_router
from .database import init_db

app = FastAPI(
    title="Korean Learning API",
    description="API for Korean language learning platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api")


# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    await init_db()


@app.get("/api/health", tags=["health"])
async def health_check():
    return {"status": "healthy"}
