"""FastAPI application for ClarityLab AI Learning Agent. Main entry point."""
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
from typing import Optional

from config.settings import get_settings
from config.logger import setup_logger
from api.api_routes import router

# Setup logging
settings = get_settings()
logger = setup_logger("main", level=settings.log_level)

# Create FastAPI app
app = FastAPI(
    title="ClarityLab AI Learning Agent",
    description="Multimodal AI system for explaining complex topics with diagrams, animations, and narration",
    version="1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix="/api")

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "ClarityLab AI Learning Agent",
        "version": "1.0"
    }

# Configuration endpoint
@app.get("/config", tags=["System"])
async def get_config() -> dict:
    """Get application configuration (non-sensitive)."""
    return {
        "debug_mode": settings.debug_mode,
        "model": settings.model_name,
        "version": "1.0"
    }

# Global exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    logger.error(f"HTTP exception: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "error": exc.detail
        }
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    """Execute startup tasks."""
    logger.info("ClarityLab AI Learning Agent starting up")
    logger.info(f"Using model: {settings.model_name}")
    logger.info(f"Debug mode: {settings.debug_mode}")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Execute shutdown tasks."""
    logger.info("Application shutting down")

if __name__ == "__main__":
    import uvicorn
    import os

    # Get port from environment variable for Cloud Run compatibility
    port = int(os.environ.get("PORT", 8080))

    logger.info(f"Starting ClarityLab AI Learning Agent API on port {port}")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level=settings.log_level.lower()
    )