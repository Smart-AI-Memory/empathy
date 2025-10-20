"""
Main entry point for the Empathy Framework Backend API.
FastAPI application with all routes and middleware configured.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import API routers
from api import auth, users, wizards, subscriptions, analysis

# Create FastAPI application
app = FastAPI(
    title="Empathy Framework API",
    description="Backend API for the Empathy Framework - Level 4 Anticipatory AI",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(wizards.router)
app.include_router(subscriptions.router)
app.include_router(analysis.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Empathy Framework API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/api/docs"
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "services": {
            "auth": "operational",
            "wizards": "operational",
            "analysis": "operational"
        }
    }


@app.get("/api/info")
async def api_info():
    """API information endpoint."""
    return {
        "name": "Deep Study AI - Empathy Framework",
        "description": "Level 4 Anticipatory AI for Software Development",
        "version": "1.0.0",
        "plugins": {
            "software": {
                "name": "Software Development Plugin",
                "wizards": ["Enhanced Testing", "Performance Profiling", "Security Analysis"]
            },
            "healthcare": {
                "name": "Healthcare Plugin",
                "wizards": ["Patient Trajectory", "Treatment Optimization", "Risk Assessment"]
            }
        },
        "documentation": "https://docs.empathyframework.ai",
        "github": "https://github.com/deepstudyai/empathy-framework"
    }


if __name__ == "__main__":
    # Run with uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
