from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
import redis
import json
from datetime import datetime, timedelta

from app.core.config import settings
from app.models.service import Service
from app.services.payment_service import PaymentService


class ProxyService:
    def __init__(self, payment_service: PaymentService):
        self.payment_service = payment_service
        self.redis_client = redis.from_url(settings.REDIS_URL)
    
    async def check_rate_limit(self, service_id: str, user_address: str) -> bool:
        """Check if user has exceeded rate limit for service"""
        service_key = f"rate_limit:{service_id}:{user_address}"
        
        try:
            current_requests = self.redis_client.get(service_key)
            if current_requests is None:
                # First request, set counter
                self.redis_client.setex(service_key, 60, 1)  # 1 minute window
                return True
            
            current_count = int(current_requests)
            service = Service.query.filter(Service.id == service_id).first()
            
            if current_count >= service.rate_limit:
                return False
            
            # Increment counter
            self.redis_client.incr(service_key)
            return True
            
        except Exception as e:
            print(f"Rate limit check error: {e}")
            return True  # Allow request on error
    
    def generate_proxy_url(self, service_id: str) -> str:
        """Generate proxy URL for service"""
        base_url = "https://api.tokenlab.io"  # Your proxy domain
        return f"{base_url}/proxy/{service_id}"
    
    async def route_request(
        self,
        db: Session,
        service_id: str,
        user_address: str,
        request_payload: Dict[str, Any],
        payment_signature: str,
        nonce: str
    ) -> Dict[str, Any]:
        """Route request through payment verification"""
        
        # Check rate limiting
        if not await self.check_rate_limit(service_id, user_address):
            raise Exception("Rate limit exceeded")
        
        # Get service details
        service = db.query(Service).filter(
            Service.id == service_id, 
            Service.is_active == True
        ).first()
        
        if not service:
            raise Exception("Service not found or inactive")
        
        # Create transaction for payment verification
        transaction_data = TransactionCreate(
            service_id=service_id,
            user_address=user_address,
            amount=service.base_price,
            currency=service.currency,
            nonce=nonce,
            request_data=request_payload
        )
        
        # Verify and process payment
        transaction = await self.payment_service.verify_and_process_payment(
            db, transaction_data, payment_signature
        )
        
        if not transaction:
            raise Exception("Payment verification failed")
        
        # Execute service request
        response_data = await self.payment_service.execute_service_request(
            db, transaction, request_payload
        )
        
        return {
            "transaction_id": transaction.id,
            "status": "success",
            "data": response_data
        }