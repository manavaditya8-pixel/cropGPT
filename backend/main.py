"""
CropGPT Backend Application
Main FastAPI application entry point for farmer assistant API
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
import os
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import init_db
from app.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    await init_db()
    print("🚀 CropGPT Backend started successfully")
    yield
    # Shutdown
    print("🛑 CropGPT Backend shutting down")


# Create FastAPI application
app = FastAPI(
    title="CropGPT Farmer Assistant API",
    description="Bilingual agricultural assistant API for farmers in Jharkhand",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api")

# Mount static files for frontend
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "application": "CropGPT Farmer Assistant",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }


# Root endpoint - serves frontend
@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main frontend application"""
    try:
        with open("frontend/templates/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse("""
        <html>
            <head><title>CropGPT - Farmer Assistant</title></head>
            <body>
                <h1>🌾 CropGPT Farmer Assistant</h1>
                <p>Backend API is running. Frontend is being set up...</p>
                <p><a href="/docs">API Documentation</a></p>
            </body>
        </html>
        """)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )