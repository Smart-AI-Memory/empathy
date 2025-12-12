"""
Empathy Memory Panel API Server

FastAPI server that provides HTTP endpoints for the VS Code extension.
This server wraps the MemoryControlPanel class and exposes its functionality via REST API.

Usage:
    python api_server_example.py

Requirements:
    pip install fastapi uvicorn

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import sys
from pathlib import Path

try:
    import uvicorn
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
except ImportError:
    print("Error: FastAPI and uvicorn are required.")
    print("Install with: pip install fastapi uvicorn")
    sys.exit(1)

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from empathy_os.memory import ControlPanelConfig, MemoryControlPanel
except ImportError:
    print("Error: Could not import MemoryControlPanel.")
    print("Make sure you're running from the Empathy Framework directory.")
    sys.exit(1)

# Create FastAPI app
app = FastAPI(
    title="Empathy Memory Panel API",
    description="REST API for Empathy Framework memory management",
    version="1.0.0",
)

# Enable CORS for VS Code extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize control panel
config = ControlPanelConfig()
panel = MemoryControlPanel(config)


@app.get("/api/ping")
async def ping():
    """Health check endpoint."""
    return {"status": "ok", "service": "empathy-memory-panel"}


@app.get("/api/status")
async def get_status():
    """Get memory system status."""
    try:
        return panel.status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats")
async def get_stats():
    """Get detailed statistics."""
    try:
        stats = panel.get_statistics()
        # Convert dataclass to dict
        from dataclasses import asdict

        return asdict(stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/redis/start")
async def start_redis():
    """Start Redis if not running."""
    try:
        status = panel.start_redis(verbose=False)
        return {
            "success": status.available,
            "message": status.message,
            "method": status.method.value,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/redis/stop")
async def stop_redis():
    """Stop Redis (if we started it)."""
    try:
        success = panel.stop_redis()
        return {
            "success": success,
            "message": (
                "Redis stopped"
                if success
                else "Could not stop Redis (may not have been started by us)"
            ),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/patterns")
async def list_patterns(classification: str | None = None, limit: int = 100):
    """List patterns with optional filtering."""
    try:
        patterns = panel.list_patterns(classification=classification, limit=limit)
        return patterns
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/patterns/{pattern_id}")
async def get_pattern(pattern_id: str):
    """Get a specific pattern."""
    try:
        # Note: This requires implementing get_pattern in MemoryControlPanel
        # For now, return a placeholder
        raise HTTPException(status_code=501, detail="Pattern retrieval not yet implemented")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/patterns/{pattern_id}")
async def delete_pattern(pattern_id: str):
    """Delete a pattern."""
    try:
        success = panel.delete_pattern(pattern_id)
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/patterns/export")
async def export_patterns(classification: str | None = None):
    """Export patterns (returns data directly)."""
    try:
        patterns = panel.list_patterns(classification=classification)
        import datetime

        return {
            "pattern_count": len(patterns),
            "export_data": {
                "patterns": patterns,
                "exported_at": datetime.datetime.utcnow().isoformat() + "Z",
                "classification_filter": classification,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check():
    """Run comprehensive health check."""
    try:
        return panel.health_check()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/memory/clear")
async def clear_memory(body: dict):
    """Clear short-term memory for an agent."""
    try:
        agent_id = body.get("agent_id", "admin")
        keys_deleted = panel.clear_short_term(agent_id=agent_id)
        return {"keys_deleted": keys_deleted}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    print("=" * 60)
    print("Empathy Memory Panel API Server")
    print("=" * 60)
    print("\nStarting server on http://localhost:8765")
    print("Press Ctrl+C to stop\n")
    print("API Documentation: http://localhost:8765/docs")
    print("Health Check: http://localhost:8765/api/ping")
    print("=" * 60 + "\n")

    uvicorn.run(app, host="localhost", port=8765, log_level="info")
