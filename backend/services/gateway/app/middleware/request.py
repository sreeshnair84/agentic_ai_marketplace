"""
Middleware for request/response processing
"""

from fastapi import Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
import time
import logging
import uuid
from typing import Callable

from ..core.database import get_database

logger = logging.getLogger(__name__)


class RequestMiddleware(BaseHTTPMiddleware):
    """Middleware for request processing and logging"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Log request
        start_time = time.time()
        logger.info(
            f"Request {request_id}: {request.method} {request.url} "
            f"from {request.client.host if request.client else 'unknown'}"
        )
        
        # Add request ID to headers
        request.headers.__dict__["_list"].append(
            (b"x-request-id", request_id.encode())
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Add headers to response
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)
            
            # Log response
            logger.info(
                f"Response {request_id}: {response.status_code} "
                f"in {process_time:.4f}s"
            )
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Error {request_id}: {str(e)} in {process_time:.4f}s"
            )
            raise


class DatabaseMiddleware(BaseHTTPMiddleware):
    """Middleware for database session management"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip database for health checks and static content
        if request.url.path in ["/health", "/ready", "/live", "/"]:
            return await call_next(request)
        
        # Create database session
        try:
            db_gen = get_database()
            db = await db_gen.__anext__()
            request.state.db = db
            
            response = await call_next(request)
            
            # Close database session
            await db_gen.aclose()
            
            return response
            
        except Exception as e:
            # Ensure database session is closed on error
            if hasattr(request.state, 'db'):
                try:
                    await db_gen.aclose()
                except:
                    pass
            raise


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware for adding security headers"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response
