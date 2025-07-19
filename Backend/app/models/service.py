from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import uuid


class Service(Base):
    __tablename__ = "services"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    provider_address = Column(String(42), nullable=False)  # Ethereum address
    endpoint_url = Column(String(500), nullable=False)
    proxy_url = Column(String(500))  # Generated proxy URL
    
    # Pricing
    pricing_model = Column(String(50), nullable=False)  # per_call, per_token, tiered
    base_price = Column(Float, nullable=False)  # Price in wei or tokens
    currency = Column(String(10), default="ETH")
    
    # Service metadata
    category = Column(String(100))
    tags = Column(JSON)  # Array of tags
    api_spec = Column(JSON)  # OpenAPI spec or custom format
    
    # Status and settings
    is_active = Column(Boolean, default=True)
    rate_limit = Column(Integer, default=10)  # requests per minute
    timeout = Column(Integer, default=30)  # seconds
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    transactions = relationship("Transaction", back_populates="service")
    analytics = relationship("ServiceAnalytics", back_populates="service")


class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    service_id = Column(String, ForeignKey("services.id"), nullable=False)
    user_address = Column(String(42), nullable=False)
    
    # Transaction details
    amount = Column(Float, nullable=False)  # Amount paid
    currency = Column(String(10), nullable=False)
    tx_hash = Column(String(66))  # Blockchain transaction hash
    nonce = Column(String(64), nullable=False)  # Anti-replay nonce
    
    # Request details
    request_data = Column(JSON)
    response_data = Column(JSON)
    status = Column(String(20), default="pending")  # pending, completed, failed
    error_message = Column(Text)
    
    # Timing
    request_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    completion_timestamp = Column(DateTime(timezone=True))
    processing_time_ms = Column(Integer)
    
    # Relationships
    service = relationship("Service", back_populates="transactions")


class ServiceAnalytics(Base):
    __tablename__ = "service_analytics"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    service_id = Column(String, ForeignKey("services.id"), nullable=False)
    
    # Metrics
    date = Column(DateTime(timezone=True), nullable=False)
    total_requests = Column(Integer, default=0)
    successful_requests = Column(Integer, default=0)
    failed_requests = Column(Integer, default=0)
    total_revenue = Column(Float, default=0.0)
    avg_response_time_ms = Column(Float, default=0.0)
    
    # Relationships
    service = relationship("Service", back_populates="analytics")

