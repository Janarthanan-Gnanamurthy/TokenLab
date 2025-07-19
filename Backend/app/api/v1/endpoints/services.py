from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.models.service import Service
from app.schemas.service import ServiceCreate, ServiceUpdate, ServiceResponse
from app.services.web3_service import Web3Service
from app.services.proxy_service import ProxyService

router = APIRouter()

# Initialize services
web3_service = Web3Service()
proxy_service = ProxyService(None)  # Will be properly initialized


@router.post("/", response_model=ServiceResponse)
async def create_service(
    service_data: ServiceCreate,
    db: Session = Depends(get_db)
):
    """Register a new AI service"""
    
    # Create service in database
    service = Service(
        **service_data.dict()
    )
    
    # Generate proxy URL
    service.proxy_url = proxy_service.generate_proxy_url(service.id)
    
    db.add(service)
    db.commit()
    db.refresh(service)
    
    # Register service on blockchain
    try:
        tx_hash = await web3_service.register_service(
            service_id=service.id,
            provider_address=service.provider_address,
            price=int(service.base_price * 10**18),  # Convert to wei
            metadata_uri=f"https://api.tokenlab.io/services/{service.id}/metadata"
        )
        
        if not tx_hash:
            # Rollback database changes if blockchain registration fails
            db.delete(service)
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to register service on blockchain"
            )
            
    except Exception as e:
        db.delete(service)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Blockchain registration failed: {str(e)}"
        )
    
    return service


@router.get("/", response_model=List[ServiceResponse])
async def list_services(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    provider_address: Optional[str] = None,
    is_active: Optional[bool] = True,
    db: Session = Depends(get_db)
):
    """List all registered services with filtering"""
    
    query = db.query(Service)
    
    if category:
        query = query.filter(Service.category == category)
    if provider_address:
        query = query.filter(Service.provider_address == provider_address.lower())
    if is_active is not None:
        query = query.filter(Service.is_active == is_active)
    
    services = query.offset(skip).limit(limit).all()
    return services


@router.get("/{service_id}", response_model=ServiceResponse)
async def get_service(service_id: str, db: Session = Depends(get_db)):
    """Get service details by ID"""
    
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    return service


@router.put("/{service_id}", response_model=ServiceResponse)
async def update_service(
    service_id: str,
    service_update: ServiceUpdate,
    db: Session = Depends(get_db)
):
    """Update service details (only by provider)"""
    
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    # Update fields
    update_data = service_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(service, field, value)
    
    db.commit()
    db.refresh(service)
    
    return service


@router.delete("/{service_id}")
async def delete_service(service_id: str, db: Session = Depends(get_db)):
    """Delete/deactivate a service"""
    
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    # Soft delete by deactivating
    service.is_active = False
    db.commit()
    
    return {"message": "Service deactivated successfully"}
