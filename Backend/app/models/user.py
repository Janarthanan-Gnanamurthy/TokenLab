from sqlalchemy import Column, String, Boolean, DateTime, JSON, Integer
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    wallet_address = Column(String(42), unique=True, nullable=False)
    
    # Profile
    username = Column(String(50), unique=True)
    email = Column(String(255))
    bio = Column(String(500))
    
    # Roles and permissions
    is_provider = Column(Boolean, default=False)
    is_consumer = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    
    # Gamification
    points = Column(Integer, default=0)
    badges = Column(JSON, default=list)  # Array of earned badges
    level = Column(Integer, default=1)
    
    # Preferences
    preferred_currency = Column(String(10), default="ETH")
    api_key = Column(String(64))  # For API access
    rate_limit_tier = Column(String(20), default="basic")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))

