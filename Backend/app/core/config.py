from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres123@metis.c1o4a8yukdml.eu-north-1.rds.amazonaws.com:5432/postgres"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Web3
    HYPERION_RPC_URL: str = "https://hyperion-testnet.rpc.url"
    PRIVATE_KEY: str = ""  # For contract interactions
    SERVICE_REGISTRY_CONTRACT: str = ""
    PAYMENT_PROCESSOR_CONTRACT: str = ""
    PROXY_CONTROLLER_CONTRACT: str = ""
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds
    
    # Proxy Settings
    PROXY_TIMEOUT: int = 30
    MAX_CONCURRENT_REQUESTS: int = 100

    class Config:
        env_file = ".env"


settings = Settings()
