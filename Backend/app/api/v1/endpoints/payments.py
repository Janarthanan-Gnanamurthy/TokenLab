from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.models.service import Transaction
from app.schemas.transaction import TransactionResponse

router = APIRouter()


@router.get("/transactions", response_model=List[TransactionResponse])
async def get_user_transactions(
    user_address: str,
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get transaction history for a user"""
    
    query = db.query(Transaction).filter(
        Transaction.user_address == user_address.lower()
    )
    
    if status_filter:
        query = query.filter(Transaction.status == status_filter)
    
    transactions = query.order_by(
        Transaction.request_timestamp.desc()
    ).offset(skip).limit(limit).all()
    
    return transactions


@router.get("/transactions/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: str,
    db: Session = Depends(get_db)
):
    """Get transaction details by ID"""
    
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id
    ).first()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    return transaction


@router.get("/revenue/{provider_address}")
async def get_provider_revenue(
    provider_address: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get revenue analytics for a provider"""
    
    from app.models.service import Service
    from sqlalchemy import func, and_
    from datetime import datetime
    
    # Get provider's services
    services = db.query(Service).filter(
        Service.provider_address == provider_address.lower()
    ).all()
    
    service_ids = [service.id for service in services]
    
    query = db.query(
        func.sum(Transaction.amount).label('total_revenue'),
        func.count(Transaction.id).label('total_transactions'),
        func.count(
            func.case([(Transaction.status == 'completed', 1)])
        ).label('successful_transactions')
    ).filter(Transaction.service_id.in_(service_ids))
    
    # Apply date filters if provided
    if start_date:
        start_dt = datetime.fromisoformat(start_date)
        query = query.filter(Transaction.request_timestamp >= start_dt)
    
    if end_date:
        end_dt = datetime.fromisoformat(end_date)
        query = query.filter(Transaction.request_timestamp <= end_dt)
    
    result = query.first()
    
    return {
        "provider_address": provider_address,
        "total_revenue": float(result.total_revenue or 0),
        "total_transactions": result.total_transactions or 0,
        "successful_transactions": result.successful_transactions or 0,
        "success_rate": (
            (result.successful_transactions / result.total_transactions * 100)
            if result.total_transactions > 0 else 0
        )
    }