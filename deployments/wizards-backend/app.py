"""
Empathy Dev Wizards - FastAPI Backend

Web API for development wizards: debugging, security analysis, code review,
and code inspection pipeline.

Deployment: Railway (wizards.smartaimemory.com)

Copyright 2025 Smart AI Memory, LLC
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from routers import code_review, debugging, health, inspect, security

# Create FastAPI app
app = FastAPI(
    title="Empathy Dev Wizards",
    description="AI-powered development wizards for debugging, security, and code quality",
    version="2.2.9",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# CORS configuration
allowed_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "https://wizards.smartaimemory.com,https://smartaimemory.com,http://localhost:3000,http://localhost:8000",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(health.router)
app.include_router(debugging.router)
app.include_router(security.router)
app.include_router(code_review.router)
app.include_router(inspect.router)

# Mount static files
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")


@app.get("/")
async def root():
    """Serve the dashboard."""
    index_path = static_path / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {
        "name": "Empathy Dev Wizards",
        "version": "2.2.9",
        "status": "running",
        "docs": "/api/docs",
    }


@app.get("/favicon.ico")
async def favicon():
    """Serve favicon."""
    favicon_path = static_path / "favicon.ico"
    if favicon_path.exists():
        return FileResponse(favicon_path)
    return {"status": "no favicon"}


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
