from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional

from app.core.database import get_db
from app.services.proxy_service import ProxyService
from app.services.payment_service import PaymentService
from app.services.web3_service import Web3Service

router = APIRouter()

# Initialize services
web3_service = Web3Service()
payment_service = PaymentService(web3_service)
proxy_service = ProxyService(payment_service)


@router.post("/{service_id}")
async def proxy_request(
    service_id: str,
    request_payload: Dict[str, Any],
    db: Session = Depends(get_db),
    user_address: str = Header(..., alias="X-User-Address"),
    payment_signature: str = Header(..., alias="X-Payment-Signature"),
    nonce: str = Header(..., alias="X-Nonce")
):
    """
    Proxy endpoint for AI service requests
    Requires payment verification before forwarding request
    """
    
    try:
        result = await proxy_service.route_request(
            db=db,
            service_id=service_id,
            user_address=user_address,
            request_payload=request_payload,
            payment_signature=payment_signature,
            nonce=nonce
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{service_id}/metadata")
async def get_service_metadata(
    service_id: str,
    db: Session = Depends(get_db)
):
    """Get service metadata for blockchain reference"""
    
    from app.models.service import Service
    
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    return {
        "id": service.id,
        "name": service.name,
        "description": service.description,
        "provider": service.provider_address,
        "pricing": {
            "model": service.pricing_model,
            "base_price": service.base_price,
            "currency": service.currency
        },
        "category": service.category,
        "tags": service.tags,
        "rate_limit": service.rate_limit,
        "timeout": service.timeout,
        "api_spec": service.api_spec
    }
