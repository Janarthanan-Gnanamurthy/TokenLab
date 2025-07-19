from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.service import Service, Transaction, ServiceAnalytics

router = APIRouter()


@router.get("/services/{service_id}/stats")
async def get_service_analytics(
    service_id: str,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get analytics for a specific service"""
    
    from sqlalchemy import func
    
    # Get service
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Get transaction stats
    stats = db.query(
        func.count(Transaction.id).label('total_requests'),
        func.sum(
            func.case([(Transaction.status == 'completed', 1)], else_=0)
        ).label('successful_requests'),
        func.sum(Transaction.amount).label('total_revenue'),
        func.avg(Transaction.processing_time_ms).label('avg_response_time')
    ).filter(
        Transaction.service_id == service_id,
        Transaction.request_timestamp >= start_date
    ).first()
    
    # Get daily breakdown
    daily_stats = db.query(
        func.date(Transaction.request_timestamp).label('date'),
        func.count(Transaction.id).label('requests'),
        func.sum(Transaction.amount).label('revenue')
    ).filter(
        Transaction.service_id == service_id,
        Transaction.request_timestamp >= start_date
    ).group_by(
        func.date(Transaction.request_timestamp)
    ).all()
    
    return {
        "service_id": service_id,
        "period_days": days,
        "total_requests": stats.total_requests or 0,
        "successful_requests": stats.successful_requests or 0,
        "total_revenue": float(stats.total_revenue or 0),
        "avg_response_time_ms": float(stats.avg_response_time or 0),
        "success_rate": (
            (stats.successful_requests / stats.total_requests * 100)
            if stats.total_requests > 0 else 0
        ),
        "daily_breakdown": [
            {
                "date": str(day.date),
                "requests": day.requests,
                "revenue": float(day.revenue)
            }
            for day in daily_stats
        ]
    }


@router.get("/marketplace/stats")
async def get_marketplace_stats(db: Session = Depends(get_db)):
    """Get overall marketplace statistics"""
    
    from sqlalchemy import func
    
    # Service stats
    service_stats = db.query(
        func.count(Service.id).label('total_services'),
        func.count(
            func.case([(Service.is_active == True, 1)])
        ).label('active_services'),
        func.count(func.distinct(Service.provider_address)).label('unique_providers')
    ).first()
    
    # Transaction stats (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    transaction_stats = db.query(
        func.count(Transaction.id).label('total_transactions'),
        func.sum(Transaction.amount).label('total_volume'),
        func.count(func.distinct(Transaction.user_address)).label('unique_users')
    ).filter(
        Transaction.request_timestamp >= thirty_days_ago
    ).first()
    
    # Top categories
    top_categories = db.query(
        Service.category,
        func.count(Service.id).label('service_count')
    ).filter(
        Service.category.isnot(None),
        Service.is_active == True
    ).group_by(Service.category).order_by(
        func.count(Service.id).desc()
    ).limit(5).all()
    
    return {
        "services": {
            "total": service_stats.total_services or 0,
            "active": service_stats.active_services or 0,
            "providers": service_stats.unique_providers or 0
        },
        "transactions_30d": {
            "count": transaction_stats.total_transactions or 0,
            "volume": float(transaction_stats.total_volume or 0),
            "unique_users": transaction_stats.unique_users or 0
        },
        "top_categories": [
            {
                "category": cat.category,
                "service_count": cat.service_count
            }
            for cat in top_categories
        ]
    }
