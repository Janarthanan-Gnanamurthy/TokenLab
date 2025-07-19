from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import time
import redis
import logging
from typing import Callable

from app.core.config import settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Redis client for rate limiting
redis_client = redis.from_url(settings.REDIS_URL)


class RateLimitMiddleware:
    """Rate limiting middleware"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        client_ip = request.client.host
        
        # Create rate limit key
        rate_limit_key = f"rate_limit:{client_ip}"
        
        try:
            # Check current request count
            current_requests = redis_client.get(rate_limit_key)
            
            if current_requests is None:
                # First request from this IP
                redis_client.setex(
                    rate_limit_key, 
                    settings.RATE_LIMIT_WINDOW, 
                    1
                )
            else:
                current_count = int(current_requests)
                if current_count >= settings.RATE_LIMIT_REQUESTS:
                    # Rate limit exceeded
                    response = JSONResponse(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        content={"detail": "Rate limit exceeded"}
                    )
                    await response(scope, receive, send)
                    return
                
                # Increment counter
                redis_client.incr(rate_limit_key)
        
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            # Continue processing on Redis errors
        
        await self.app(scope, receive, send)


class LoggingMiddleware:
    """Request logging middleware"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        start_time = time.time()
        
        # Log request
        logger.info(
            f"Request: {request.method} {request.url.path} "
            f"from {request.client.host}"
        )
        
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                process_time = time.time() - start_time
                logger.info(
                    f"Response: {message['status']} "
                    f"({process_time:.3f}s)"
                )
            await send(message)
        
        await self.app(scope, receive, send_wrapper)