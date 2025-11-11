"""
Performance Profiling Wizard - Live Demonstration

Shows performance analysis and bottleneck prediction.

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
"""

import asyncio
import json

# Mock profiling data for demonstration
MOCK_PROFILE_DATA = json.dumps(
    {
        "functions": [
            {
                "name": "process_user_data",
                "file": "/app/api.py",
                "line": 42,
                "total_time": 2.5,
                "self_time": 0.3,
                "calls": 150,
                "cumulative_time": 2.5,
                "percent": 45.0,
            },
            {
                "name": "fetch_user_posts",
                "file": "/app/database.py",
                "line": 105,
                "total_time": 1.8,
                "self_time": 0.1,
                "calls": 1500,  # High call count - potential N+1!
                "cumulative_time": 1.8,
                "percent": 32.0,
            },
            {
                "name": "calculate_recommendations",
                "file": "/app/recommendations.py",
                "line": 78,
                "total_time": 0.8,
                "self_time": 0.8,
                "calls": 10,
                "cumulative_time": 0.8,
                "percent": 14.0,
            },
            {
                "name": "send_notification",
                "file": "/app/notifications.py",
                "line": 23,
                "total_time": 0.4,
                "self_time": 0.4,
                "calls": 50,
                "cumulative_time": 0.4,
                "percent": 7.0,
            },
        ]
    }
)

# Mock performance metrics over time
MOCK_METRICS_HISTORY = [
    {"time": "day1", "response_time": 0.2, "throughput": 150, "error_rate": 0.001},
    {"time": "day2", "response_time": 0.35, "throughput": 140, "error_rate": 0.002},
    {"time": "day3", "response_time": 0.55, "throughput": 125, "error_rate": 0.004},
    {"time": "day4", "response_time": 0.8, "throughput": 110, "error_rate": 0.007},
]

CURRENT_METRICS = {
    "response_time": 0.95,  # Approaching 1s timeout!
    "throughput": 95,
    "error_rate": 0.010,
    "cpu_usage": 0.75,
    "memory_usage": 0.82,
}


async def demo_basic_profiling():
    """Demo 1: Basic Performance Profiling"""
    print("=" * 70)
    print("DEMO 1: Basic Performance Profiling Analysis")
    print("=" * 70)

    from empathy_software_plugin.wizards.performance_profiling_wizard import (
        PerformanceProfilingWizard,
    )

    wizard = PerformanceProfilingWizard()

    result = await wizard.analyze(
        {"profiler_data": MOCK_PROFILE_DATA, "profiler_type": "simple_json"}
    )

    summary = result["profiling_summary"]

    print("\n📊 Profiling Summary:")
    print(f"  Total Functions: {summary['total_functions']}")
    print(f"  Total Time: {summary['total_time']:.2f}s")

    print("\n🐌 Top 5 Slowest Functions:")
    for func in summary["top_5_slowest"]:
        print(f"  {func['function']}: {func['time']:.2f}s ({func['percent']:.1f}%)")

    print("\n" + "=" * 70)


async def demo_bottleneck_detection():
    """Demo 2: Bottleneck Detection"""
    print("\n" + "=" * 70)
    print("DEMO 2: Bottleneck Detection")
    print("=" * 70)

    from empathy_software_plugin.wizards.performance_profiling_wizard import (
        PerformanceProfilingWizard,
    )

    wizard = PerformanceProfilingWizard()

    result = await wizard.analyze(
        {
            "profiler_data": MOCK_PROFILE_DATA,
            "profiler_type": "simple_json",
            "threshold_percent": 5.0,
        }
    )

    bottlenecks = result["bottlenecks"]

    print(f"\n⚠️  BOTTLENECKS DETECTED: {len(bottlenecks)}\n")

    for bottleneck in bottlenecks:
        print(f"  [{bottleneck['severity']}] {bottleneck['type'].upper()}")
        print(f"      Function: {bottleneck['function_name']}")
        print(
            f"      Time Cost: {bottleneck['time_cost']:.2f}s ({bottleneck['percent_total']:.1f}%)"
        )
        print(f"      Reason: {bottleneck['reasoning']}")
        print(f"      Fix: {bottleneck['fix_suggestion']}")
        print()

    print("=" * 70)


async def demo_trajectory_prediction():
    """Demo 3: Level 4 - Performance Trajectory Prediction"""
    print("\n" + "=" * 70)
    print("DEMO 3: Level 4 - Performance Trajectory Prediction")
    print("=" * 70)

    from empathy_software_plugin.wizards.performance_profiling_wizard import (
        PerformanceProfilingWizard,
    )

    wizard = PerformanceProfilingWizard()

    result = await wizard.analyze(
        {
            "profiler_data": MOCK_PROFILE_DATA,
            "profiler_type": "simple_json",
            "current_metrics": CURRENT_METRICS,
            "historical_metrics": MOCK_METRICS_HISTORY,
        }
    )

    trajectory = result["trajectory"]

    if trajectory:
        print("\n📈 Trajectory Analysis:")
        print(f"  State: {trajectory['trajectory_state'].upper()}")
        print(f"  Confidence: {trajectory['confidence']:.2f}")

        if trajectory["estimated_time_to_critical"]:
            print(f"  ⏰ Time to Critical: {trajectory['estimated_time_to_critical']}")

        print("\n📊 Performance Trends:")
        for trend in trajectory["trends"]:
            if trend["concerning"]:
                print(f"  ⚠️  {trend['metric_name']}: {trend['direction']}")
                print(f"      Current: {trend['current_value']:.3f}")
                print(f"      Change: {trend['change']:+.3f} ({trend['change_percent']:+.1f}%)")
                print(f"      {trend['reasoning']}")

        print("\n🔮 Assessment:")
        print(f"  {trajectory['overall_assessment']}")

    print("\n" + "=" * 70)


async def demo_predictions():
    """Demo 4: Level 4 Predictions"""
    print("\n" + "=" * 70)
    print("DEMO 4: Level 4 - Performance Predictions")
    print("=" * 70)

    from empathy_software_plugin.wizards.performance_profiling_wizard import (
        PerformanceProfilingWizard,
    )

    wizard = PerformanceProfilingWizard()

    result = await wizard.analyze(
        {
            "profiler_data": MOCK_PROFILE_DATA,
            "profiler_type": "simple_json",
            "current_metrics": CURRENT_METRICS,
            "historical_metrics": MOCK_METRICS_HISTORY,
        }
    )

    print("\n🔮 PREDICTIONS:\n")

    for pred in result["predictions"]:
        print(f"  Type: {pred['type'].upper()}")
        print(f"  Severity: {pred['severity'].upper()}")
        print(f"  {pred['description']}")

        if "affected_functions" in pred:
            print("\n  Affected Functions:")
            for func in pred["affected_functions"]:
                print(f"    - {func}")

        if "prevention_steps" in pred:
            print("\n  Prevention Steps:")
            for step in pred["prevention_steps"]:
                print(f"    - {step}")
        print()

    print("=" * 70)


async def demo_insights():
    """Demo 5: Performance Insights"""
    print("\n" + "=" * 70)
    print("DEMO 5: Performance Insights & Optimization Potential")
    print("=" * 70)

    from empathy_software_plugin.wizards.performance_profiling_wizard import (
        PerformanceProfilingWizard,
    )

    wizard = PerformanceProfilingWizard()

    result = await wizard.analyze(
        {"profiler_data": MOCK_PROFILE_DATA, "profiler_type": "simple_json"}
    )

    insights = result["insights"]

    print("\n📊 Performance Insights:")
    print(f"  Dominant Pattern: {insights['dominant_pattern']}")
    print(f"  I/O Bound Operations: {insights['io_bound_operations']}")
    print(f"  CPU Bound Operations: {insights['cpu_bound_operations']}")
    print(f"  N+1 Query Patterns: {insights['n_plus_one_queries']}")

    print("\n💡 Optimization Potential:")
    opt = insights["optimization_potential"]
    print(f"  Potential Savings: {opt['potential_savings']:.2f}s")
    print(f"  Percentage: {opt['percentage']:.1f}%")
    print(f"  Assessment: {opt['assessment']}")

    print("\n📝 Recommendations:")
    for rec in result["recommendations"][:5]:
        print(f"  • {rec}")

    print("\n" + "=" * 70)


async def demo_the_value():
    """Demo 6: Show the Value"""
    print("\n" + "=" * 70)
    print("DEMO 6: The Value - Anticipatory Performance Management")
    print("=" * 70)

    print("\n" + "TRADITIONAL PROFILING".center(70))
    print("-" * 70)
    print("✓ process_user_data: 2.5s")
    print("✓ fetch_user_posts: 1.8s")
    print("")
    print("Status: Profiled ✓")
    print("")
    print("...but what do you do with this information?")

    print("\n" + "PERFORMANCE PROFILING WIZARD".center(70))
    print("-" * 70)
    print("✓ process_user_data: 2.5s (45% of total)")
    print("✓ fetch_user_posts: 1.8s (32% of total, 1500 calls)")
    print("")
    print("⚠️  CRITICAL: Hot path detected - 45% of execution time")
    print("⚠️  HIGH: N+1 query pattern - 1500 database calls")
    print("⚠️  TRAJECTORY: Response time trending toward timeout")
    print("")
    print("PREDICTION: Will hit 1s timeout in ~2 days at current rate")
    print("")
    print("In our experience, N+1 database queries cause exponential")
    print("slowdown as data grows. Fix now to prevent outages.")

    print("\n" + "THE DIFFERENCE".center(70))
    print("-" * 70)
    print("Profiling tells you WHERE time is spent.")
    print("Performance Wizard tells you WHAT to fix and WHY it matters.")
    print("")
    print("It predicts performance problems BEFORE they cause outages.")

    print("\n" + "=" * 70)


async def main():
    """Run all demos"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 9 + "PERFORMANCE PROFILING WIZARD - DEMONSTRATIONS" + " " * 14 + "║")
    print("║" + " " * 16 + "Bottleneck Detection & Prediction" + " " * 19 + "║")
    print("╚" + "=" * 68 + "╝")

    await demo_basic_profiling()
    await demo_bottleneck_detection()
    await demo_trajectory_prediction()
    await demo_predictions()
    await demo_insights()
    await demo_the_value()

    print("\n" + "=" * 70)
    print("DEMOS COMPLETE")
    print("=" * 70)
    print("\nKey Features Demonstrated:")
    print("  ✅ Profiling data parsing (cProfile, Chrome DevTools)")
    print("  ✅ Bottleneck detection (hot paths, N+1 queries, I/O)")
    print("  ✅ Level 4: Performance trajectory prediction")
    print("  ✅ Level 4: Predicts degradation before critical")
    print("  ✅ Optimization potential estimation")
    print("\nIn our experience, N+1 database queries and unoptimized hot paths")
    print("cause the majority of performance issues. This wizard helps you")
    print("identify and fix them BEFORE they cause production outages.")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
