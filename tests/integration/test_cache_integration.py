"""Integration test for cache with BaseWorkflow.

Tests that caching works end-to-end with real workflows.
"""

import asyncio

import pytest

from empathy_os.cache import create_cache
from empathy_os.workflows.code_review import CodeReviewWorkflow


@pytest.mark.asyncio
async def test_code_review_with_cache():
    """Test that code review workflow uses cache correctly."""
    # Create cache instance (hash-only for simplicity)
    cache = create_cache(cache_type="hash")

    # Create workflow with cache
    workflow = CodeReviewWorkflow(
        use_crew=False,  # Disable crew for faster testing
        cache=cache,
        enable_cache=True,
    )

    # Test input
    test_diff = """
    diff --git a/src/auth.py b/src/auth.py
    index 1234567..abcdefg 100644
    --- a/src/auth.py
    +++ b/src/auth.py
    @@ -10,5 +10,6 @@ def authenticate(username, password):
         if user is None:
             return False
    +    # Added password validation
         return user.verify_password(password)
    """

    # First execution - should miss cache
    result1 = await workflow.execute(
        diff=test_diff,
        files_changed=["src/auth.py"],
        is_core_module=False,
    )

    assert result1.success
    cost_report1 = result1.cost_report

    # Should have some cache misses on first run
    print("\nFirst run:")
    print(f"  Cache hits: {cost_report1.cache_hits}")
    print(f"  Cache misses: {cost_report1.cache_misses}")
    print(f"  Cache hit rate: {cost_report1.cache_hit_rate:.1f}%")
    print(f"  Total cost: ${cost_report1.total_cost:.6f}")

    # Second execution - should hit cache
    result2 = await workflow.execute(
        diff=test_diff,
        files_changed=["src/auth.py"],
        is_core_module=False,
    )

    assert result2.success
    cost_report2 = result2.cost_report

    print("\nSecond run:")
    print(f"  Cache hits: {cost_report2.cache_hits}")
    print(f"  Cache misses: {cost_report2.cache_misses}")
    print(f"  Cache hit rate: {cost_report2.cache_hit_rate:.1f}%")
    print(f"  Total cost: ${cost_report2.total_cost:.6f}")
    print(f"  Savings from cache: ${cost_report2.savings_from_cache:.6f}")

    # Verify cache effectiveness
    # Second run should have more cache hits than first
    assert cost_report2.cache_hits > cost_report1.cache_hits
    # Hit rate should be higher on second run
    assert cost_report2.cache_hit_rate > cost_report1.cache_hit_rate


@pytest.mark.asyncio
async def test_cache_disabled():
    """Test that workflow works correctly with caching disabled."""
    workflow = CodeReviewWorkflow(
        use_crew=False,
        enable_cache=False,
    )

    test_diff = """
    diff --git a/src/test.py b/src/test.py
    index 1234567..abcdefg 100644
    --- a/src/test.py
    +++ b/src/test.py
    @@ -1,3 +1,4 @@
    +# Added comment
     def test():
         pass
    """

    result = await workflow.execute(
        diff=test_diff,
        files_changed=["src/test.py"],
        is_core_module=False,
    )

    assert result.success
    # Cache metrics should all be zero when disabled
    assert result.cost_report.cache_hits == 0
    assert result.cost_report.cache_misses == 0
    assert result.cost_report.cache_hit_rate == 0.0


if __name__ == "__main__":
    # Run tests manually for quick verification
    print("Testing cache integration with code-review workflow...")
    print("=" * 60)

    asyncio.run(test_code_review_with_cache())

    print("\n" + "=" * 60)
    print("Testing with cache disabled...")
    asyncio.run(test_cache_disabled())

    print("\n✅ All cache integration tests passed!")
