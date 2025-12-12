"""
Quick API test script for Empathy Memory Dashboard.

Tests all major endpoints to verify the API is working correctly.

Usage:
    python test_api.py
"""

import asyncio
import sys

try:
    import httpx
except ImportError:
    print("Error: httpx not installed. Install with: pip install httpx")
    sys.exit(1)

BASE_URL = "http://localhost:8000"


async def test_api():
    """Test all API endpoints."""
    print("=" * 70)
    print("Empathy Memory Dashboard API - Test Suite")
    print("=" * 70)
    print()

    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test 1: Root endpoint
        print("[1/8] Testing root endpoint...")
        try:
            response = await client.get(f"{BASE_URL}/")
            assert response.status_code == 200
            data = response.json()
            print(f"  ✓ API: {data['name']} v{data['version']}")
            print(f"  ✓ Status: {data['status']}")
            print()
        except Exception as e:
            print(f"  ✗ Failed: {e}")
            print()

        # Test 2: Ping
        print("[2/8] Testing ping endpoint...")
        try:
            response = await client.get(f"{BASE_URL}/ping")
            assert response.status_code == 200
            data = response.json()
            print(f"  ✓ {data['message']}")
            print()
        except Exception as e:
            print(f"  ✗ Failed: {e}")
            print()

        # Test 3: Status
        print("[3/8] Testing status endpoint...")
        try:
            response = await client.get(f"{BASE_URL}/api/status")
            assert response.status_code == 200
            data = response.json()
            print(f"  ✓ Redis: {data['redis']['status']}")
            print(f"  ✓ Storage: {data['long_term']['status']}")
            print(f"  ✓ Patterns: {data['long_term']['pattern_count']}")
            print()
        except Exception as e:
            print(f"  ✗ Failed: {e}")
            print()

        # Test 4: Statistics
        print("[4/8] Testing statistics endpoint...")
        try:
            response = await client.get(f"{BASE_URL}/api/stats")
            assert response.status_code == 200
            data = response.json()
            print(f"  ✓ Redis keys: {data['redis_keys_total']}")
            print(f"  ✓ Patterns: {data['patterns_total']}")
            print(f"  ✓ Memory: {data['redis_memory_used']}")
            print()
        except Exception as e:
            print(f"  ✗ Failed: {e}")
            print()

        # Test 5: Health check
        print("[5/8] Testing health check endpoint...")
        try:
            response = await client.get(f"{BASE_URL}/api/health")
            assert response.status_code == 200
            data = response.json()
            print(f"  ✓ Overall: {data['overall']}")
            print(f"  ✓ Checks: {len(data['checks'])} performed")
            if data["recommendations"]:
                print(f"  ⚠ Recommendations: {len(data['recommendations'])}")
                for rec in data["recommendations"]:
                    print(f"    - {rec}")
            print()
        except Exception as e:
            print(f"  ✗ Failed: {e}")
            print()

        # Test 6: List patterns
        print("[6/8] Testing list patterns endpoint...")
        try:
            response = await client.get(f"{BASE_URL}/api/patterns", params={"limit": 10})
            assert response.status_code == 200
            data = response.json()
            print(f"  ✓ Total patterns: {data['total']}")
            print(f"  ✓ Returned: {len(data['patterns'])}")
            print()
        except Exception as e:
            print(f"  ✗ Failed: {e}")
            print()

        # Test 7: Start Redis (if not running)
        print("[7/8] Testing Redis start endpoint...")
        try:
            response = await client.post(f"{BASE_URL}/api/redis/start", json={"verbose": False})
            assert response.status_code == 200
            data = response.json()
            if data["success"]:
                print(f"  ✓ Redis started via: {data['method']}")
            else:
                print("  ℹ Redis already running or unavailable")
            print()
        except Exception as e:
            print(f"  ✗ Failed: {e}")
            print()

        # Test 8: Export patterns
        print("[8/8] Testing export patterns endpoint...")
        try:
            response = await client.post(
                f"{BASE_URL}/api/patterns/export",
                json={"classification": None, "output_filename": "test_export.json"},
            )
            assert response.status_code == 200
            data = response.json()
            print(f"  ✓ Exported {data['pattern_count']} patterns")
            print(f"  ✓ Output: {data['output_path']}")
            print()
        except Exception as e:
            print(f"  ✗ Failed: {e}")
            print()

    print("=" * 70)
    print("Test suite completed!")
    print("=" * 70)


def main():
    """Main entry point."""
    print()
    print("Make sure the API is running on http://localhost:8000")
    print("Start it with: uvicorn dashboard.backend.main:app --reload")
    print()
    input("Press Enter to start tests...")
    print()

    try:
        asyncio.run(test_api())
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
    except Exception as e:
        print(f"\n\nError running tests: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
