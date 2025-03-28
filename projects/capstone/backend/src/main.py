from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import router as api_router
from .database import init_db
from .utils.data_loader import load_initial_data
from .database import AsyncSessionLocal

app = FastAPI(
    title="HagXwon",
    description="HagXwon - Your Korean Learning Journey",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api")


# Initialize database and load initial data on startup
@app.on_event("startup")
async def startup_event():
    await init_db()  # Initialize database tables
    async with AsyncSessionLocal() as session:
        await load_initial_data(session)  # Load initial data into tables


@app.get("/api/health", tags=["health"])
async def health_check():
    return {"status": "healthy"}
