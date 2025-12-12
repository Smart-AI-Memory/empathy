# Empathy Memory Dashboard API

Production-ready FastAPI backend for managing and monitoring the Empathy Framework memory system.

## Features

- **REST API**: Complete CRUD operations for memory management
- **WebSocket**: Real-time metrics streaming
- **Authentication**: JWT-based auth (optional, configurable)
- **CORS**: Configured for local development
- **OpenAPI**: Auto-generated documentation
- **Structured Logging**: JSON-formatted logs with structlog
- **Type Safety**: Full Pydantic validation
- **Async**: Non-blocking operations throughout

## Architecture

```
backend/
├── main.py                 # FastAPI app entry point
├── config.py              # Settings management
├── schemas.py             # Pydantic models
├── requirements.txt       # Python dependencies
├── api/
│   ├── __init__.py       # API router aggregation
│   ├── memory.py         # Memory system endpoints
│   ├── patterns.py       # Pattern management endpoints
│   └── websocket.py      # WebSocket handler
└── services/
    └── memory_service.py # Business logic layer
```

## Installation

### Prerequisites

- Python 3.11+
- Empathy Framework installed
- Redis (optional, auto-starts)

### Setup

1. **Install dependencies**:

```bash
cd /Users/patrickroebuck/empathy_11_6_2025/Empathy-framework/dashboard/backend
pip install -r requirements.txt
```

2. **Configure environment** (optional):

Create `.env` file:

```bash
# Environment
ENVIRONMENT=development
DEBUG=true

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_AUTO_START=true

# Storage
STORAGE_DIR=./memdocs_storage
AUDIT_DIR=./logs
ENCRYPTION_ENABLED=true

# Security (set in production!)
JWT_SECRET_KEY=your-secret-key-here
AUTH_ENABLED=false

# WebSocket
METRICS_UPDATE_INTERVAL=5
```

3. **Run the server**:

```bash
# Development (auto-reload)
uvicorn dashboard.backend.main:app --reload --host 0.0.0.0 --port 8000

# Or use the built-in runner
python -m dashboard.backend.main

# Production
uvicorn dashboard.backend.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Documentation

Once running, access interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## API Endpoints

### Memory System

#### `GET /api/status`

Get system status (Redis, storage, configuration).

**Response**:
```json
{
  "timestamp": "2025-01-15T12:34:56.789Z",
  "redis": {
    "status": "running",
    "host": "localhost",
    "port": 6379,
    "method": "homebrew"
  },
  "long_term": {
    "status": "available",
    "storage_dir": "./memdocs_storage",
    "pattern_count": 42
  },
  "config": {
    "auto_start_redis": true,
    "audit_dir": "./logs"
  }
}
```

#### `POST /api/redis/start`

Start Redis if not running.

**Request**:
```json
{
  "verbose": true
}
```

**Response**:
```json
{
  "success": true,
  "available": true,
  "method": "homebrew",
  "message": "Redis started via homebrew"
}
```

#### `POST /api/redis/stop`

Stop Redis (if started by system).

**Response**:
```json
{
  "success": true,
  "message": "Redis stopped successfully"
}
```

#### `GET /api/stats`

Get comprehensive statistics.

**Response**:
```json
{
  "redis_available": true,
  "redis_method": "homebrew",
  "redis_keys_total": 150,
  "redis_keys_working": 100,
  "redis_keys_staged": 5,
  "redis_memory_used": "2.5M",
  "long_term_available": true,
  "patterns_total": 42,
  "patterns_public": 30,
  "patterns_internal": 10,
  "patterns_sensitive": 2,
  "patterns_encrypted": 2,
  "collected_at": "2025-01-15T12:34:56.789Z"
}
```

#### `GET /api/health`

Health check with recommendations.

**Response**:
```json
{
  "overall": "healthy",
  "checks": [
    {
      "name": "redis",
      "status": "pass",
      "message": "Redis is running"
    },
    {
      "name": "long_term",
      "status": "pass",
      "message": "Storage available"
    }
  ],
  "recommendations": []
}
```

### Pattern Management

#### `GET /api/patterns`

List patterns with optional filtering.

**Query Parameters**:
- `classification` (optional): PUBLIC, INTERNAL, or SENSITIVE
- `limit` (optional): Max patterns to return (default: 100)

**Response**:
```json
{
  "total": 42,
  "patterns": [
    {
      "pattern_id": "pat_abc123",
      "pattern_type": "algorithm",
      "classification": "INTERNAL",
      "created_at": "2025-01-15T12:34:56.789Z",
      "user_id": "dev@company.com"
    }
  ],
  "classification_filter": null
}
```

#### `POST /api/patterns/export`

Export patterns to JSON file.

**Request**:
```json
{
  "classification": "PUBLIC",
  "output_filename": "patterns_backup.json"
}
```

**Response**:
```json
{
  "success": true,
  "pattern_count": 30,
  "output_path": "/tmp/patterns_backup.json",
  "exported_at": "2025-01-15T12:34:56.789Z"
}
```

#### `GET /api/patterns/export/download/{filename}`

Download previously exported file.

#### `DELETE /api/patterns/{pattern_id}`

Delete a pattern (admin only).

**Query Parameters**:
- `user_id` (optional): User performing deletion (default: admin@system)

**Response**:
```json
{
  "success": true
}
```

### WebSocket

#### `WS /ws/metrics`

Real-time metrics streaming.

**Server sends**:
```json
{
  "type": "metrics",
  "data": {
    "redis_keys_total": 150,
    "redis_keys_working": 100,
    "redis_keys_staged": 5,
    "redis_memory_used": "2.5M",
    "patterns_total": 42,
    "timestamp": "2025-01-15T12:34:56.789Z"
  },
  "timestamp": "2025-01-15T12:34:56.789Z"
}
```

**Client can send**:
```json
{
  "type": "ping"
}
```

## Usage Examples

### Python Client

```python
import httpx

# Get status
async with httpx.AsyncClient() as client:
    response = await client.get("http://localhost:8000/api/status")
    status = response.json()
    print(f"Redis: {status['redis']['status']}")

# Start Redis
async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/api/redis/start",
        json={"verbose": True}
    )
    result = response.json()
    print(f"Started via: {result['method']}")

# List patterns
async with httpx.AsyncClient() as client:
    response = await client.get(
        "http://localhost:8000/api/patterns",
        params={"classification": "PUBLIC", "limit": 10}
    )
    patterns = response.json()
    print(f"Found {patterns['total']} patterns")
```

### JavaScript/TypeScript Client

```javascript
// Get status
const response = await fetch('http://localhost:8000/api/status');
const status = await response.json();
console.log('Redis:', status.redis.status);

// WebSocket connection
const ws = new WebSocket('ws://localhost:8000/ws/metrics');

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  if (message.type === 'metrics') {
    console.log('Metrics:', message.data);
  }
};

// Request immediate update
ws.send(JSON.stringify({ type: 'ping' }));
```

### cURL Examples

```bash
# Get status
curl http://localhost:8000/api/status

# Start Redis
curl -X POST http://localhost:8000/api/redis/start \
  -H "Content-Type: application/json" \
  -d '{"verbose": true}'

# Get statistics
curl http://localhost:8000/api/stats

# List patterns (filtered)
curl "http://localhost:8000/api/patterns?classification=PUBLIC&limit=10"

# Export patterns
curl -X POST http://localhost:8000/api/patterns/export \
  -H "Content-Type: application/json" \
  -d '{"classification": "PUBLIC"}'
```

## Development

### Running Tests

```bash
# Install dev dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=dashboard.backend --cov-report=html
```

### Code Quality

```bash
# Format code
black dashboard/backend/

# Lint
ruff check dashboard/backend/

# Type check
mypy dashboard/backend/
```

### Hot Reload

Development server automatically reloads on code changes:

```bash
uvicorn dashboard.backend.main:app --reload
```

## Security

### Authentication

Enable JWT authentication:

```bash
# .env
JWT_SECRET_KEY=your-very-secret-key
AUTH_ENABLED=true
```

### CORS

Configure allowed origins:

```bash
# .env
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
```

### Production Checklist

- [ ] Set `ENVIRONMENT=production`
- [ ] Set strong `JWT_SECRET_KEY`
- [ ] Configure `CORS_ORIGINS` for your domain
- [ ] Disable debug mode (`DEBUG=false`)
- [ ] Set up HTTPS (reverse proxy)
- [ ] Configure rate limiting
- [ ] Set up monitoring/logging
- [ ] Review audit logs regularly

## Deployment

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "dashboard.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: empathy-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: empathy-api
  template:
    metadata:
      labels:
        app: empathy-api
    spec:
      containers:
      - name: api
        image: empathy-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: REDIS_HOST
          value: "redis-service"
```

## Troubleshooting

### Redis Won't Start

```bash
# Check if Redis is already running
redis-cli ping

# Install Redis (macOS)
brew install redis
brew services start redis

# Install Redis (Linux)
sudo apt install redis-server
sudo systemctl start redis
```

### CORS Errors

Add your frontend origin to `.env`:

```bash
CORS_ORIGINS=http://localhost:3000
```

### Import Errors

Ensure Empathy Framework is in Python path:

```bash
export PYTHONPATH=/Users/patrickroebuck/empathy_11_6_2025/Empathy-framework/src:$PYTHONPATH
```

## Support

- **Documentation**: http://localhost:8000/docs
- **Issues**: GitHub repository
- **Email**: empathy-framework@company.com

## License

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
