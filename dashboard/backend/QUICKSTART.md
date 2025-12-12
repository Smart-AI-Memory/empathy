# Quick Start Guide

Get the Empathy Memory Dashboard API running in 60 seconds.

## Option 1: Automated Setup (Recommended)

```bash
cd /Users/patrickroebuck/empathy_11_6_2025/Empathy-framework/dashboard/backend
./run.sh
```

This script will:
1. Create a virtual environment
2. Install all dependencies
3. Start the development server with auto-reload

## Option 2: Manual Setup

### 1. Install Dependencies

```bash
cd /Users/patrickroebuck/empathy_11_6_2025/Empathy-framework/dashboard/backend
pip install -r requirements.txt
```

### 2. Start the Server

```bash
uvicorn dashboard.backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Access the API

Open your browser to:
- **Interactive Docs**: http://localhost:8000/docs
- **API Root**: http://localhost:8000/

## Test the API

Run the test suite:

```bash
# In another terminal, while the server is running
python test_api.py
```

## Common Endpoints

### Get System Status
```bash
curl http://localhost:8000/api/status
```

### Start Redis
```bash
curl -X POST http://localhost:8000/api/redis/start \
  -H "Content-Type: application/json" \
  -d '{"verbose": true}'
```

### Get Statistics
```bash
curl http://localhost:8000/api/stats
```

### List Patterns
```bash
curl "http://localhost:8000/api/patterns?limit=10"
```

### Health Check
```bash
curl http://localhost:8000/api/health
```

## WebSocket Test

```javascript
// In browser console or Node.js
const ws = new WebSocket('ws://localhost:8000/ws/metrics');

ws.onmessage = (event) => {
  console.log('Metrics:', JSON.parse(event.data));
};
```

## Troubleshooting

### Port Already in Use

```bash
# Change port
uvicorn dashboard.backend.main:app --reload --port 8001
```

### Import Errors

```bash
# Add Empathy Framework to Python path
export PYTHONPATH=/Users/patrickroebuck/empathy_11_6_2025/Empathy-framework/src:$PYTHONPATH
```

### Redis Not Starting

The API will automatically try to start Redis. If it fails, install manually:

```bash
# macOS
brew install redis
brew services start redis

# Linux
sudo apt install redis-server
sudo systemctl start redis
```

## Next Steps

1. Read the full [README.md](README.md) for detailed documentation
2. Explore the interactive API docs at http://localhost:8000/docs
3. Check out the example client code in the README
4. Configure your frontend to connect to the API

## Configuration

Create a `.env` file (copy from `.env.example`):

```bash
cp .env.example .env
```

Edit `.env` to customize:
- CORS origins for your frontend
- Redis connection settings
- Storage directories
- Security settings

## Production Deployment

See [README.md](README.md#deployment) for production deployment guides including:
- Docker
- Kubernetes
- Security checklist
- Performance tuning
