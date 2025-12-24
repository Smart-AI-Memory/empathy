# Resilience Patterns

Production-ready patterns for fault tolerance and reliability. These patterns help your application handle failures gracefully, prevent cascading failures, and maintain service availability.

## Overview

```python
from empathy_os.resilience import (
    retry,              # Retry failed operations
    circuit_breaker,    # Prevent cascading failures
    timeout,            # Prevent hanging operations
    fallback,           # Graceful degradation
    HealthCheck,        # Monitor system health
)
```

## Retry with Exponential Backoff

Automatically retry failed operations with increasing delays:

```python
from empathy_os.resilience import retry, RetryConfig

@retry(max_attempts=3, initial_delay=1.0, backoff_factor=2.0)
async def call_external_api():
    response = await api.get("/data")
    return response.json()
```

### How Backoff Works

With `initial_delay=1.0` and `backoff_factor=2.0`:

| Attempt | Delay Before Retry |
|---------|-------------------|
| 1 | 0s (immediate) |
| 2 | 1.0s |
| 3 | 2.0s |
| 4 | 4.0s |
| 5 | 8.0s (capped at max_delay) |

### Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `max_attempts` | `3` | Maximum retry attempts |
| `initial_delay` | `1.0` | Initial delay in seconds |
| `backoff_factor` | `2.0` | Multiply delay by this each retry |
| `max_delay` | `60.0` | Maximum delay cap |
| `jitter` | `True` | Add randomness to prevent thundering herd |

### Jitter

Jitter adds randomness to prevent all clients from retrying simultaneously:

```python
# Without jitter: All clients retry at exactly 1s, 2s, 4s...
# With jitter: Clients retry at ~0.8s, ~2.3s, ~3.7s...

@retry(max_attempts=3, jitter=True)  # Recommended for distributed systems
async def call_api():
    ...
```

---

## Circuit Breaker

Prevent cascading failures by failing fast when a service is down:

```python
from empathy_os.resilience import circuit_breaker, CircuitOpenError

@circuit_breaker(
    name="external_api",
    failure_threshold=5,    # Open after 5 failures
    reset_timeout=60.0,     # Try again after 60s
    half_open_max_calls=3   # 3 successes to fully close
)
async def call_external_api():
    return await api.get("/data")
```

### Circuit States

```
     ┌─────────┐
     │ CLOSED  │ ◄─── Normal operation
     └────┬────┘
          │ failures >= threshold
          ▼
     ┌─────────┐
     │  OPEN   │ ◄─── Fail immediately
     └────┬────┘
          │ after reset_timeout
          ▼
   ┌───────────────┐
   │  HALF_OPEN    │ ◄─── Testing recovery
   └───────┬───────┘
           │
     ┌─────┴─────┐
     │           │
   success    failure
     │           │
     ▼           ▼
  CLOSED       OPEN
```

### With Fallback

```python
async def cached_fallback():
    return {"status": "cached", "data": cache.get("last_known")}

@circuit_breaker(
    name="api",
    failure_threshold=3,
    fallback=cached_fallback
)
async def get_data():
    return await api.get("/data")

# When circuit is open, cached_fallback() is called instead of raising
```

### Monitoring Circuit State

```python
from empathy_os.resilience import get_circuit_breaker

cb = get_circuit_breaker("external_api")

print(f"State: {cb.state}")           # CLOSED, OPEN, HALF_OPEN
print(f"Failures: {cb.get_stats()['failure_count']}")
print(f"Resets in: {cb.get_time_until_reset()}s")
```

---

## Timeout

Prevent operations from hanging indefinitely:

```python
from empathy_os.resilience import timeout, with_timeout, ResilienceTimeoutError

@timeout(30.0)  # 30 second timeout
async def slow_operation():
    return await long_running_task()
```

### With Fallback

```python
@timeout(5.0, fallback=lambda: "default_value")
async def quick_lookup():
    return await cache.get("key")
```

### One-off Timeout

```python
from empathy_os.resilience import with_timeout

result = await with_timeout(
    some_coroutine(),
    timeout_seconds=10.0,
    fallback_value="timeout_default"
)
```

---

## Fallback Chain

Graceful degradation with multiple fallback options:

```python
from empathy_os.resilience import Fallback, fallback

# Decorator approach
@fallback(fallback_func=get_cached_data, default="No data available")
async def get_live_data():
    return await api.get("/live")
```

### Fallback Chain

Try multiple sources in order:

```python
fb = Fallback(name="data_source", default_value="offline_mode")

@fb.add
async def primary_api():
    return await api1.get("/data")

@fb.add
async def backup_api():
    return await api2.get("/data")

@fb.add
async def local_cache():
    return cache.get("data")

# Tries primary → backup → cache → default
result = await fb.execute()
```

---

## Health Checks

Monitor system component health:

```python
from empathy_os.resilience import HealthCheck, HealthStatus

health = HealthCheck(version="3.1.0")

@health.register("database", timeout=5.0)
async def check_database():
    await db.ping()
    return True  # Healthy

@health.register("cache", timeout=2.0)
async def check_cache():
    return {
        "healthy": redis.ping(),
        "connections": redis.info()["connected_clients"],
        "memory_mb": redis.info()["used_memory_mb"]
    }

@health.register("external_api", timeout=10.0)
async def check_api():
    response = await api.get("/health")
    return response.status_code == 200
```

### Running Health Checks

```python
# Run all checks
system_health = await health.run_all()

print(f"Status: {system_health.status}")  # HEALTHY, DEGRADED, UNHEALTHY
print(f"Uptime: {system_health.uptime_seconds}s")
print(f"Version: {system_health.version}")

# Serialize for API response
return system_health.to_dict()
```

### Health Check Return Values

```python
# Boolean - simple healthy/unhealthy
@health.register("simple")
async def simple_check():
    return True  # or False

# Dict - with details
@health.register("detailed")
async def detailed_check():
    return {
        "healthy": True,
        "connections": 42,
        "latency_ms": 15
    }

# Exception - unhealthy with error message
@health.register("error")
async def error_check():
    raise RuntimeError("Database connection failed")
    # Caught and reported as unhealthy
```

---

## Combining Patterns

Stack decorators for robust services:

```python
from empathy_os.resilience import retry, circuit_breaker, timeout, fallback

async def cached_fallback():
    return cache.get("last_known_good")

@circuit_breaker(name="api", failure_threshold=5)
@retry(max_attempts=3, initial_delay=0.5)
@timeout(10.0)
@fallback(cached_fallback)
async def reliable_api_call():
    return await external_api.get("/data")
```

### Execution Order

1. **fallback** - Catches any unhandled exception, returns fallback
2. **timeout** - Cancels if takes too long
3. **retry** - Retries on failure (within timeout)
4. **circuit_breaker** - Fails fast if circuit is open

---

## Best Practices

### 1. Use Jitter for Distributed Systems

```python
@retry(max_attempts=5, jitter=True)
async def distributed_call():
    ...
```

### 2. Name Circuit Breakers

```python
# Good: Named for the service being protected
@circuit_breaker(name="payment_gateway")

# Bad: Default name (function name)
@circuit_breaker()
```

### 3. Set Appropriate Timeouts

```python
# API calls: 5-30 seconds
@timeout(10.0)
async def api_call(): ...

# Database queries: 1-5 seconds
@timeout(3.0)
async def db_query(): ...

# Background tasks: 60+ seconds
@timeout(300.0)
async def batch_process(): ...
```

### 4. Log Circuit State Changes

The circuit breaker automatically logs state transitions:

```
INFO  Circuit breaker 'api' transitioning to HALF_OPEN
WARN  Circuit breaker 'api' OPEN after 5 failures
INFO  Circuit breaker 'api' CLOSED - service recovered
```

### 5. Monitor Health Endpoints

```python
from fastapi import FastAPI
from empathy_os.resilience import HealthCheck

app = FastAPI()
health = HealthCheck(version="3.1.0")

@app.get("/health")
async def health_endpoint():
    status = await health.run_all()
    return status.to_dict()
```

---

## See Also

- [API Reference](../API_REFERENCE.md#resilience-patterns) - Full API documentation
- [Smart Router](smart-router.md) - Natural language wizard dispatch
- [Memory Graph](memory-graph.md) - Cross-wizard knowledge sharing
