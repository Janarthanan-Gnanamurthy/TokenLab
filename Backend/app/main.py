from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1.api import api_router
from app.core.middleware import RateLimitMiddleware, LoggingMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting TokenLab API...")
    yield
    # Shutdown
    print("Shutting down TokenLab API...")


app = FastAPI(
    title="TokenLab API",
    description="Monetization protocol for AI services on Hyperion",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(LoggingMiddleware)

# Include API router
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "TokenLab API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
