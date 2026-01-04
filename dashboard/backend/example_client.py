"""Example API Client for Empathy Memory Dashboard

Demonstrates how to interact with the API using Python.
Can be used as a reference for building your own clients.

Usage:
    python example_client.py

Requirements:
    pip install httpx websockets
"""

import asyncio
import json
from typing import Any

try:
    import httpx
    import websockets
except ImportError:
    print("Error: Missing dependencies. Install with:")
    print("  pip install httpx websockets")
    exit(1)


class EmpathyMemoryClient:
    """Async client for Empathy Memory Dashboard API.

    Example:
        >>> async with EmpathyMemoryClient("http://localhost:8000") as client:
        ...     status = await client.get_status()
        ...     print(f"Redis: {status['redis']['status']}")

    """

    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize client.

        Args:
            base_url: Base URL of the API (default: http://localhost:8000)

        """
        self.base_url = base_url.rstrip("/")
        self.client: httpx.AsyncClient | None = None

    async def __aenter__(self):
        """Async context manager entry."""
        self.client = httpx.AsyncClient(timeout=30.0)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.client:
            await self.client.aclose()

    # ========================================================================
    # Memory System Operations
    # ========================================================================

    async def get_status(self) -> dict[str, Any]:
        """Get system status.

        Returns:
            Status dictionary with Redis and storage info

        """
        response = await self.client.get(f"{self.base_url}/api/status")
        response.raise_for_status()
        return response.json()

    async def start_redis(self, verbose: bool = True) -> dict[str, Any]:
        """Start Redis if not running.

        Args:
            verbose: Enable verbose logging

        Returns:
            Start result with method and status

        """
        response = await self.client.post(
            f"{self.base_url}/api/redis/start",
            json={"verbose": verbose},
        )
        response.raise_for_status()
        return response.json()

    async def stop_redis(self) -> dict[str, Any]:
        """Stop Redis if we started it.

        Returns:
            Stop result

        """
        response = await self.client.post(f"{self.base_url}/api/redis/stop")
        response.raise_for_status()
        return response.json()

    async def get_statistics(self) -> dict[str, Any]:
        """Get comprehensive statistics.

        Returns:
            Statistics dictionary with Redis and pattern metrics

        """
        response = await self.client.get(f"{self.base_url}/api/stats")
        response.raise_for_status()
        return response.json()

    async def health_check(self) -> dict[str, Any]:
        """Perform health check.

        Returns:
            Health check results with recommendations

        """
        response = await self.client.get(f"{self.base_url}/api/health")
        response.raise_for_status()
        return response.json()

    # ========================================================================
    # Pattern Operations
    # ========================================================================

    async def list_patterns(
        self,
        classification: str | None = None,
        limit: int = 100,
    ) -> dict[str, Any]:
        """List patterns.

        Args:
            classification: Filter by PUBLIC/INTERNAL/SENSITIVE
            limit: Maximum patterns to return

        Returns:
            Pattern list with metadata

        """
        params = {"limit": limit}
        if classification:
            params["classification"] = classification

        response = await self.client.get(f"{self.base_url}/api/patterns", params=params)
        response.raise_for_status()
        return response.json()

    async def export_patterns(
        self,
        classification: str | None = None,
        output_filename: str | None = None,
    ) -> dict[str, Any]:
        """Export patterns to JSON file.

        Args:
            classification: Filter by classification
            output_filename: Custom output filename

        Returns:
            Export result with path and count

        """
        payload = {}
        if classification:
            payload["classification"] = classification
        if output_filename:
            payload["output_filename"] = output_filename

        response = await self.client.post(f"{self.base_url}/api/patterns/export", json=payload)
        response.raise_for_status()
        return response.json()

    async def delete_pattern(
        self,
        pattern_id: str,
        user_id: str = "admin@system",
    ) -> dict[str, Any]:
        """Delete a pattern.

        Args:
            pattern_id: Pattern ID to delete
            user_id: User performing deletion

        Returns:
            Success status

        """
        response = await self.client.delete(
            f"{self.base_url}/api/patterns/{pattern_id}",
            params={"user_id": user_id},
        )
        response.raise_for_status()
        return response.json()

    # ========================================================================
    # WebSocket Operations
    # ========================================================================

    async def stream_metrics(
        self,
        callback,
        duration_seconds: int | None = None,
    ):
        """Stream real-time metrics via WebSocket.

        Args:
            callback: Async function to call with each metric update
            duration_seconds: Optional duration to stream (None = indefinite)

        Example:
            >>> async def print_metrics(data):
            ...     print(f"Keys: {data['redis_keys_total']}")
            >>> await client.stream_metrics(print_metrics, duration_seconds=10)

        """
        ws_url = self.base_url.replace("http://", "ws://").replace("https://", "wss://")
        ws_url = f"{ws_url}/ws/metrics"

        async with websockets.connect(ws_url) as websocket:
            start_time = asyncio.get_event_loop().time()

            while True:
                # Check duration
                if duration_seconds:
                    elapsed = asyncio.get_event_loop().time() - start_time
                    if elapsed >= duration_seconds:
                        break

                # Receive message
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    data = json.loads(message)

                    # Call callback with metrics
                    if data.get("type") == "metrics":
                        await callback(data["data"])

                except asyncio.TimeoutError:
                    continue
                except websockets.exceptions.ConnectionClosed:
                    break


# ============================================================================
# Example Usage
# ============================================================================


async def example_basic_operations():
    """Example: Basic memory system operations."""
    print("\n" + "=" * 70)
    print("Example 1: Basic Operations")
    print("=" * 70 + "\n")

    async with EmpathyMemoryClient() as client:
        # Get status
        print("1. Getting system status...")
        status = await client.get_status()
        print(f"   Redis: {status['redis']['status']}")
        print(f"   Storage: {status['long_term']['status']}")
        print(f"   Patterns: {status['long_term']['pattern_count']}")
        print()

        # Start Redis if needed
        if status["redis"]["status"] != "running":
            print("2. Starting Redis...")
            result = await client.start_redis()
            print(f"   Method: {result['method']}")
            print()

        # Get statistics
        print("3. Getting statistics...")
        stats = await client.get_statistics()
        print(f"   Redis keys: {stats['redis_keys_total']}")
        print(f"   Memory used: {stats['redis_memory_used']}")
        print(f"   Patterns: {stats['patterns_total']}")
        print(f"   └─ PUBLIC: {stats['patterns_public']}")
        print(f"   └─ INTERNAL: {stats['patterns_internal']}")
        print(f"   └─ SENSITIVE: {stats['patterns_sensitive']}")
        print()

        # Health check
        print("4. Running health check...")
        health = await client.health_check()
        print(f"   Overall: {health['overall']}")
        print(
            f"   Checks passed: {len([c for c in health['checks'] if c['status'] == 'pass'])}/{len(health['checks'])}",
        )
        if health["recommendations"]:
            print(f"   Recommendations: {len(health['recommendations'])}")
            for rec in health["recommendations"]:
                print(f"     - {rec}")
        print()


async def example_pattern_operations():
    """Example: Pattern management operations."""
    print("\n" + "=" * 70)
    print("Example 2: Pattern Operations")
    print("=" * 70 + "\n")

    async with EmpathyMemoryClient() as client:
        # List all patterns
        print("1. Listing all patterns...")
        result = await client.list_patterns(limit=10)
        print(f"   Total: {result['total']}")
        for pattern in result["patterns"][:5]:
            print(
                f"   - [{pattern['classification']}] {pattern['pattern_id']} ({pattern['pattern_type']})",
            )
        print()

        # List PUBLIC patterns only
        print("2. Listing PUBLIC patterns...")
        result = await client.list_patterns(classification="PUBLIC", limit=5)
        print(f"   Total PUBLIC: {result['total']}")
        print()

        # Export patterns
        print("3. Exporting patterns...")
        export_result = await client.export_patterns(
            classification=None,
            output_filename="backup.json",
        )
        print(f"   Exported: {export_result['pattern_count']} patterns")
        print(f"   Location: {export_result['output_path']}")
        print()


async def example_realtime_metrics():
    """Example: Real-time metrics streaming."""
    print("\n" + "=" * 70)
    print("Example 3: Real-time Metrics (10 seconds)")
    print("=" * 70 + "\n")

    async with EmpathyMemoryClient() as client:
        update_count = 0

        async def print_metrics(data):
            nonlocal update_count
            update_count += 1
            print(f"Update {update_count}:")
            print(f"  Redis keys: {data['redis_keys_total']}")
            print(f"  Memory: {data['redis_memory_used']}")
            print(f"  Patterns: {data['patterns_total']}")
            print(f"  Time: {data['timestamp']}")
            print()

        await client.stream_metrics(print_metrics, duration_seconds=10)

    print(f"Received {update_count} metric updates")
    print()


async def example_comprehensive():
    """Example: Comprehensive workflow."""
    print("\n" + "=" * 70)
    print("Example 4: Comprehensive Workflow")
    print("=" * 70 + "\n")

    async with EmpathyMemoryClient() as client:
        # 1. Check health
        print("Step 1: Health check...")
        health = await client.health_check()
        if health["overall"] != "healthy":
            print(f"   Warning: System is {health['overall']}")

        # 2. Ensure Redis is running
        print("\nStep 2: Ensure Redis is running...")
        status = await client.get_status()
        if status["redis"]["status"] != "running":
            await client.start_redis()
            print("   Started Redis")
        else:
            print("   Redis already running")

        # 3. Get current statistics
        print("\nStep 3: Collect baseline statistics...")
        stats = await client.get_statistics()
        baseline_patterns = stats["patterns_total"]
        print(f"   Current patterns: {baseline_patterns}")

        # 4. List patterns by classification
        print("\nStep 4: Analyze patterns by classification...")
        for classification in ["PUBLIC", "INTERNAL", "SENSITIVE"]:
            result = await client.list_patterns(classification=classification)
            print(f"   {classification}: {result['total']}")

        # 5. Export for backup
        print("\nStep 5: Create backup...")
        export = await client.export_patterns()
        print(f"   Backed up {export['pattern_count']} patterns")
        print(f"   Location: {export['output_path']}")

        print("\nWorkflow complete!")
        print()


async def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("Empathy Memory Dashboard API - Example Client")
    print("=" * 70)

    try:
        await example_basic_operations()
        await example_pattern_operations()
        # await example_realtime_metrics()  # Uncomment to test WebSocket
        await example_comprehensive()

        print("\n" + "=" * 70)
        print("All examples completed successfully!")
        print("=" * 70 + "\n")

    except httpx.HTTPError as e:
        print(f"\nHTTP Error: {e}")
        print("Make sure the API is running on http://localhost:8000")
    except Exception as e:
        print(f"\nError: {e}")


if __name__ == "__main__":
    print("\nMake sure the API is running:")
    print("  uvicorn dashboard.backend.main:app --reload\n")
    input("Press Enter to start examples...")

    asyncio.run(main())
