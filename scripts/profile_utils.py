"""Profiling utilities for Empathy Framework.

Provides decorators and helpers for performance profiling and optimization.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import cProfile
import io
import pstats
import time
from functools import wraps
from pathlib import Path
from typing import Any, Callable


def profile_function(output_file: str | None = None):
    """Decorator to profile a function with cProfile.

    Args:
        output_file: Optional path to save profile data for visualization

    Example:
        @profile_function(output_file="profiles/my_function.prof")
        def expensive_function():
            # ... code ...
            pass

        # Then visualize with: snakeviz profiles/my_function.prof
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            profiler = cProfile.Profile()
            profiler.enable()

            result = func(*args, **kwargs)

            profiler.disable()

            # Print to stdout
            s = io.StringIO()
            stats = pstats.Stats(profiler, stream=s)
            stats.sort_stats("cumulative")
            stats.print_stats(20)  # Top 20
            print(s.getvalue())

            # Save to file if requested
            if output_file:
                output_path = Path(output_file)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                stats.dump_stats(str(output_path))
                print(f"\nProfile saved to: {output_file}")
                print(f"Visualize with: snakeviz {output_file}")

            return result

        return wrapper

    return decorator


def time_function(func: Callable) -> Callable:
    """Simple timing decorator for quick performance checks.

    Example:
        @time_function
        def my_function():
            # ... code ...
            pass

        # Prints: my_function took 0.1234 seconds
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        duration = time.perf_counter() - start
        print(f"{func.__name__} took {duration:.4f} seconds")
        return result

    return wrapper


def profile_memory(func: Callable) -> Callable:
    """Decorator for memory profiling.

    Requires: pip install memory_profiler

    Example:
        @profile_memory
        def memory_intensive_function():
            # ... code ...
            pass
    """
    try:
        from memory_profiler import profile

        return profile(func)
    except ImportError:
        print("Warning: memory_profiler not installed. Install with: pip install memory_profiler")
        return func


class PerformanceMonitor:
    """Context manager for monitoring performance of code blocks.

    Example:
        with PerformanceMonitor("database query"):
            result = db.query(...)

        # Prints: database query took 0.1234 seconds
    """

    def __init__(self, name: str = "operation"):
        self.name = name
        self.start_time: float = 0
        self.end_time: float = 0

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.perf_counter()
        duration = self.end_time - self.start_time
        print(f"{self.name} took {duration:.4f} seconds")

    @property
    def duration(self) -> float:
        """Get the duration in seconds."""
        return self.end_time - self.start_time


def benchmark_comparison(func1: Callable, func2: Callable, *args, iterations: int = 100, **kwargs):
    """Compare performance of two functions.

    Args:
        func1: First function to benchmark
        func2: Second function to benchmark
        *args: Arguments to pass to both functions
        iterations: Number of iterations to run
        **kwargs: Keyword arguments to pass to both functions

    Returns:
        Dictionary with timing results and speedup factor

    Example:
        results = benchmark_comparison(
            old_implementation,
            new_implementation,
            test_data,
            iterations=1000
        )
        print(f"Speedup: {results['speedup']:.2f}x")
    """
    # Warm up
    func1(*args, **kwargs)
    func2(*args, **kwargs)

    # Benchmark func1
    start = time.perf_counter()
    for _ in range(iterations):
        func1(*args, **kwargs)
    time1 = time.perf_counter() - start

    # Benchmark func2
    start = time.perf_counter()
    for _ in range(iterations):
        func2(*args, **kwargs)
    time2 = time.perf_counter() - start

    speedup = time1 / time2 if time2 > 0 else float("inf")

    return {
        "func1_name": func1.__name__,
        "func2_name": func2.__name__,
        "func1_time": time1,
        "func2_time": time2,
        "iterations": iterations,
        "speedup": speedup,
        "improvement_pct": ((time1 - time2) / time1 * 100) if time1 > 0 else 0,
    }


def print_benchmark_results(results: dict):
    """Pretty print benchmark comparison results.

    Args:
        results: Results dictionary from benchmark_comparison()
    """
    print("\n" + "=" * 60)
    print("BENCHMARK COMPARISON RESULTS")
    print("=" * 60)
    print(f"Function 1: {results['func1_name']}")
    print(f"  Total time: {results['func1_time']:.4f}s")
    print(f"  Per iteration: {results['func1_time']/results['iterations']*1000:.4f}ms")
    print()
    print(f"Function 2: {results['func2_name']}")
    print(f"  Total time: {results['func2_time']:.4f}s")
    print(f"  Per iteration: {results['func2_time']/results['iterations']*1000:.4f}ms")
    print()
    print(f"Iterations: {results['iterations']:,}")
    print(f"Speedup: {results['speedup']:.2f}x")
    print(f"Improvement: {results['improvement_pct']:.1f}%")
    print("=" * 60)


if __name__ == "__main__":
    # Example usage
    @profile_function()
    @time_function
    def example_function():
        """Example function to demonstrate profiling."""
        total = 0
        for i in range(1000000):
            total += i
        return total

    result = example_function()
    print(f"Result: {result}")
