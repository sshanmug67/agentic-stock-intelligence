"""
Main FastAPI application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config.settings import settings
from .utils.logging_config import setup_fresh_logging, shutdown_logging
from .api.v1 import intents, executions, health


# Setup logging BEFORE anything else
setup_fresh_logging(
    log_file_name="stock_intel",
    console_level=__import__('logging').INFO
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 Starting Stock Intelligence Pipeline API")
    settings.print_summary()
    yield
    # Shutdown
    print("👋 Shutting down...")
    shutdown_logging()


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="AI agent-driven stock intelligence pipeline with intent-based execution",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix=settings.api_prefix, tags=["Health"])
app.include_router(intents.router, prefix=settings.api_prefix, tags=["Intents"])
app.include_router(executions.router, prefix=settings.api_prefix, tags=["Executions"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Stock Intelligence Pipeline API",
        "version": "0.1.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        reload_dirs=["backend"],                    # ← Only watch backend/ code
        reload_excludes=["*.log", "logs/*", "*.pyc"]  # ← Ignore log files
    )