"""
Health check endpoints
"""
from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "pipeline-backend"
    }


@router.get("/health/ready")
async def readiness_check():
    """Readiness check"""
    # Add checks for dependencies (DB, Redis, etc.)
    return {
        "ready": True,
        "dependencies": {
            "database": "ok",  # TODO: actual check
            "redis": "ok"  # TODO: actual check
        }
    }