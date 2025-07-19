from pydantic import BaseModel, HttpUrl, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class PricingModel(str, Enum):
    PER_CALL = "per_call"
    PER_TOKEN = "per_token"
    TIERED = "tiered"


class ServiceBase(BaseModel):
    name: str
    description: Optional[str] = None
    endpoint_url: HttpUrl
    pricing_model: PricingModel
    base_price: float
    currency: str = "ETH"
    category: Optional[str] = None
    tags: Optional[List[str]] = []
    rate_limit: int = 10
    timeout: int = 30


class ServiceCreate(ServiceBase):
    provider_address: str
    api_spec: Optional[Dict[str, Any]] = None
    
    @validator('provider_address')
    def validate_address(cls, v):
        if not v.startswith('0x') or len(v) != 42:
            raise ValueError('Invalid Ethereum address')
        return v.lower()


class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    endpoint_url: Optional[HttpUrl] = None
    base_price: Optional[float] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    rate_limit: Optional[int] = None
    timeout: Optional[int] = None
    is_active: Optional[bool] = None


class ServiceResponse(ServiceBase):
    id: str
    provider_address: str
    proxy_url: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True
