from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
import httpx
import time

from app.services.web3_service import Web3Service
from app.models.service import Service, Transaction
from app.schemas.transaction import TransactionCreate


class PaymentService:
    def __init__(self, web3_service: Web3Service):
        self.web3_service = web3_service
    
    async def verify_and_process_payment(
        self, 
        db: Session,
        transaction_data: TransactionCreate,
        signature: str
    ) -> Optional[Transaction]:
        """Verify payment signature and process if valid"""
        
        # Get service details
        service = db.query(Service).filter(Service.id == transaction_data.service_id).first()
        if not service or not service.is_active:
            return None
        
        # Convert amount to wei for blockchain
        amount_wei = int(transaction_data.amount * 10**18)
        
        # Verify payment signature
        is_valid = await self.web3_service.verify_payment(
            service_id=transaction_data.service_id,
            user_address=transaction_data.user_address,
            amount=amount_wei,
            nonce=transaction_data.nonce,
            signature=signature
        )
        
        if not is_valid:
            return None
        
        # Create transaction record
        transaction = Transaction(
            service_id=transaction_data.service_id,
            user_address=transaction_data.user_address,
            amount=transaction_data.amount,
            currency=transaction_data.currency,
            nonce=transaction_data.nonce,
            request_data=transaction_data.request_data,
            status="verified"
        )
        
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        
        return transaction
    
    async def execute_service_request(
        self, 
        db: Session,
        transaction: Transaction,
        request_payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute the actual service request after payment verification"""
        
        service = db.query(Service).filter(Service.id == transaction.service_id).first()
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient(timeout=service.timeout) as client:
                response = await client.post(
                    str(service.endpoint_url),
                    json=request_payload,
                    headers={"Content-Type": "application/json"}
                )
                
                response_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {"data": response.text}
                
                # Update transaction with results
                processing_time = int((time.time() - start_time) * 1000)
                transaction.response_data = response_data
                transaction.processing_time_ms = processing_time
                transaction.status = "completed" if response.status_code == 200 else "failed"
                transaction.completion_timestamp = func.now()
                
                if response.status_code != 200:
                    transaction.error_message = f"HTTP {response.status_code}: {response.text}"
                
                db.commit()
                
                return response_data
                
        except Exception as e:
            # Update transaction with error
            transaction.status = "failed"
            transaction.error_message = str(e)
            transaction.completion_timestamp = func.now()
            db.commit()
            
            raise e
