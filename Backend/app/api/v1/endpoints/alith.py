from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List
import re

from app.core.database import get_db
from app.models.service import Service
from app.services.proxy_service import ProxyService

router = APIRouter()


class AlithQueryProcessor:
    """Process natural language queries for service discovery"""
    
    def __init__(self):
        # Define patterns for different query types
        self.patterns = {
            'find_service': r'find.*?(\w+).*?(?:under|below|less than).*?(\$[\d.]+)',
            'compare_services': r'compare.*?(\w+).*?services',
            'cheapest_service': r'(?:cheapest|lowest cost).*?(\w+)',
            'best_service': r'(?:best|top|highest rated).*?(\w+)',
            'service_category': r'(\w+).*?(?:services|models|apis)'
        }
    
    def parse_query(self, query: str) -> Dict[str, Any]:
        """Parse natural language query into structured parameters"""
        query_lower = query.lower()
        
        # Extract service type/category
        categories = ['summarizer', 'translator', 'classifier', 'generator', 'analyzer']
        found_category = None
        for category in categories:
            if category in query_lower:
                found_category = category
                break
        
        # Extract price constraint
        price_match = re.search(r'\$?([\d.]+)', query)
        max_price = float(price_match.group(1)) if price_match else None
        
        # Determine query type
        if 'find' in query_lower or 'search' in query_lower:
            query_type = 'find'
        elif 'compare' in query_lower:
            query_type = 'compare'
        elif 'cheapest' in query_lower or 'lowest' in query_lower:
            query_type = 'cheapest'
        elif 'best' in query_lower or 'top' in query_lower:
            query_type = 'best'
        else:
            query_type = 'general'
        
        return {
            'type': query_type,
            'category': found_category,
            'max_price': max_price,
            'original_query': query
        }
    
    def format_service_response(self, services: List[Service]) -> Dict[str, Any]:
        """Format services for Alith response"""
        
        if not services:
            return {
                "message": "No services found matching your criteria.",
                "services": []
            }
        
        formatted_services = []
        for service in services[:5]:  # Limit to top 5 results
            formatted_services.append({
                "id": service.id,
                "name": service.name,
                "description": service.description,
                "price": f"${service.base_price} per {service.pricing_model.replace('_', ' ')}",
                "provider": service.provider_address[:10] + "...",
                "proxy_url": service.proxy_url,
                "category": service.category,
                "rating": 4.5  # Mock rating for now
            })
        
        return {
            "message": f"Found {len(services)} services matching your criteria.",
            "services": formatted_services,
            "total_count": len(services)
        }


@router.post("/query")
async def process_alith_query(
    query_data: Dict[str, str],
    db: Session = Depends(get_db)
):
    """Process natural language query from Alith"""
    
    query = query_data.get('query', '')
    if not query:
        raise HTTPException(status_code=400, detail="Query is required")
    
    processor = AlithQueryProcessor()
    parsed_query = processor.parse_query(query)
    
    # Build database query based on parsed parameters
    db_query = db.query(Service).filter(Service.is_active == True)
    
    # Apply category filter
    if parsed_query['category']:
        db_query = db_query.filter(
            Service.category.ilike(f"%{parsed_query['category']}%")
        )
    
    # Apply price filter
    if parsed_query['max_price']:
        db_query = db_query.filter(Service.base_price <= parsed_query['max_price'])
    
    # Apply sorting based on query type
    if parsed_query['type'] == 'cheapest':
        db_query = db_query.order_by(Service.base_price.asc())
    elif parsed_query['type'] == 'best':
        # For now, order by creation date (newer = potentially better)
        db_query = db_query.order_by(Service.created_at.desc())
    else:
        db_query = db_query.order_by(Service.created_at.desc())
    
    services = db_query.limit(10).all()
    
    response = processor.format_service_response(services)
    response['query_info'] = parsed_query
    
    return response


@router.post("/execute")
async def execute_alith_request(
    request_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Execute a service request through Alith"""
    
    service_id = request_data.get('service_id')
    user_address = request_data.get('user_address')
    input_data = request_data.get('input_data', {})
    
    if not all([service_id, user_address]):
        raise HTTPException(
            status_code=400, 
            detail="service_id and user_address are required"
        )
    
    # Get service details
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    # For Alith integration, we'll need to handle payment differently
    # This would typically integrate with Alith's payment system
    return {
        "service": {
            "id": service.id,
            "name": service.name,
            "proxy_url": service.proxy_url,
            "price": service.base_price,
            "currency": service.currency
        },
        "execution_info": {
            "message": "Ready to execute. Payment signature required.",
            "required_headers": [
                "X-User-Address",
                "X-Payment-Signature", 
                "X-Nonce"
            ]
        },
        "input_data": input_data
    }