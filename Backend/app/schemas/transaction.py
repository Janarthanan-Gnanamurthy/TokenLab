from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class TransactionCreate(BaseModel):
    service_id: str
    user_address: str
    amount: float
    currency: str
    nonce: str
    request_data: Optional[Dict[str, Any]] = None


class TransactionResponse(BaseModel):
    id: str
    service_id: str
    user_address: str
    amount: float
    currency: str
    tx_hash: Optional[str]
    status: str
    request_timestamp: datetime
    completion_timestamp: Optional[datetime]
    processing_time_ms: Optional[int]
    
    class Config:
        from_attributes = True