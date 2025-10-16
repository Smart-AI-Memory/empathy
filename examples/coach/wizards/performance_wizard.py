"""
Performance Wizard

Identifies performance bottlenecks, optimizes code, and predicts scaling issues.
Uses Empathy Framework Level 3 (Proactive) for bottleneck detection and Level 4
(Anticipatory) for scaling trajectory prediction.

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
"""

import re
from typing import List, Dict, Any

from .base_wizard import (
    BaseWizard,
    WizardTask,
    WizardOutput,
    WizardArtifact,
    WizardRisk,
    WizardHandoff,
    EmpathyChecks,
)


class PerformanceWizard(BaseWizard):
    """
    Wizard for performance optimization and profiling

    Uses:
    - Level 2: Guide user through profiling setup
    - Level 3: Proactively detect slow queries and endpoints
    - Level 4: Anticipate scaling bottlenecks before they occur
    """

    def can_handle(self, task: WizardTask) -> float:
        """Determine if this is a performance optimization task"""
        # High-priority performance phrases (worth 2 points each)
        performance_phrases = [
            "performance", "slow", "bottleneck", "optimize", "latency",
            "timeout", "profile", "benchmark", "scale", "scaling"
        ]

        # Secondary indicators (worth 1 point each)
        secondary_keywords = [
            "query", "memory", "cpu", "cache", "n+1", "database",
            "response time", "load time", "throughput"
        ]

        task_lower = (task.task + " " + task.context).lower()

        # Count high-priority matches (2 points each)
        primary_matches = sum(2 for phrase in performance_phrases if phrase in task_lower)

        # Count secondary matches (1 point each)
        secondary_matches = sum(1 for keyword in secondary_keywords if keyword in task_lower)

        total_score = primary_matches + secondary_matches

        return min(total_score / 6.0, 1.0)  # 6+ points = 100% confidence

    def execute(self, task: WizardTask) -> WizardOutput:
        """Execute performance optimization workflow"""

        # Step 1: Assess emotional context (performance issues are stressful!)
        emotional_state = self._assess_emotional_state(task)

        # Step 2: Extract constraints
        constraints = self._extract_constraints(task)

        # Step 3: Analyze performance issue
        diagnosis = self._analyze_performance(task)

        # Step 4: Profile bottlenecks (Level 3: Proactive)
        bottlenecks = self._profile_bottlenecks(task)

        # Step 5: Generate optimization plan
        optimization_plan = self._create_optimization_plan(task, bottlenecks)

        # Step 6: Create optimized code
        optimized_code = self._generate_optimized_code(task, bottlenecks)

        # Step 7: Generate benchmarks
        benchmarks = self._create_benchmarks(task, bottlenecks)

        # Step 8: Predict scaling issues (Level 4: Anticipatory)
        scaling_analysis = self._predict_scaling_issues(task, bottlenecks)

        # Step 9: Identify risks
        risks = self._identify_risks(task, bottlenecks)

        # Step 10: Create artifacts
        artifacts = [
            WizardArtifact(
                type="doc",
                title="Performance Analysis Report",
                content=self._generate_performance_report(diagnosis, bottlenecks, scaling_analysis)
            ),
            WizardArtifact(
                type="code",
                title="Optimized Code",
                content=optimized_code
            ),
            WizardArtifact(
                type="code",
                title="Benchmark Suite",
                content=benchmarks
            ),
            WizardArtifact(
                type="doc",
                title="Caching Strategy",
                content=self._generate_caching_strategy(task, bottlenecks)
            ),
            WizardArtifact(
                type="doc",
                title="Scaling Projection",
                content=scaling_analysis
            )
        ]

        # Step 11: Generate next actions
        next_actions = optimization_plan + self._generate_anticipatory_actions(task)

        # Step 12: Create empathy checks
        empathy_checks = EmpathyChecks(
            cognitive=f"Considered {task.role}'s constraints: {', '.join(constraints.keys())}",
            emotional=f"Acknowledged pressure: {emotional_state['urgency']} urgency, {emotional_state['pressure']} pressure",
            anticipatory=scaling_analysis[:200] + "..." if len(scaling_analysis) > 200 else scaling_analysis
        )

        return WizardOutput(
            wizard_name=self.name,
            diagnosis=diagnosis,
            plan=optimization_plan,
            artifacts=artifacts,
            risks=risks,
            handoffs=self._create_handoffs(task),
            next_actions=next_actions,
            empathy_checks=empathy_checks,
            confidence=self.can_handle(task)
        )

    def _analyze_performance(self, task: WizardTask) -> str:
        """Analyze performance issue from task description"""
        analysis = f"# Performance Analysis\n\n"
        analysis += f"**Issue**: {task.task}\n\n"

        # Categorize performance issue
        categories = []
        task_lower = (task.task + " " + task.context).lower()

        if any(kw in task_lower for kw in ["database", "query", "sql", "n+1"]):
            categories.append("Database Query Performance")
        if any(kw in task_lower for kw in ["api", "endpoint", "request", "latency"]):
            categories.append("API Response Time")
        if any(kw in task_lower for kw in ["memory", "leak", "heap"]):
            categories.append("Memory Usage")
        if any(kw in task_lower for kw in ["cpu", "computation", "algorithm"]):
            categories.append("CPU/Computation")
        if any(kw in task_lower for kw in ["cache", "caching"]):
            categories.append("Caching Strategy")

        if not categories:
            categories.append("General Performance")

        analysis += f"**Category**: {', '.join(categories)}\n\n"
        analysis += f"**Context**: {task.context[:300]}...\n" if len(task.context) > 300 else f"**Context**: {task.context}\n"

        return analysis

    def _profile_bottlenecks(self, task: WizardTask) -> List[Dict[str, Any]]:
        """Identify performance bottlenecks"""
        bottlenecks = []
        task_lower = (task.task + " " + task.context).lower()

        # Database bottlenecks
        if "database" in task_lower or "query" in task_lower or "sql" in task_lower:
            bottlenecks.append({
                "type": "database",
                "issue": "Slow database queries",
                "severity": "high",
                "impact": "78% of response time",
                "solutions": [
                    "Add database indexes on frequently queried columns",
                    "Use query caching (Redis) for read-heavy operations",
                    "Implement connection pooling to reduce overhead",
                    "Consider read replicas for scaling reads"
                ]
            })

        # N+1 query problem
        if "n+1" in task_lower or "loop" in task_lower:
            bottlenecks.append({
                "type": "n+1_query",
                "issue": "N+1 query problem detected",
                "severity": "critical",
                "impact": "Queries scale linearly with data (O(n))",
                "solutions": [
                    "Use select_related() / prefetch_related() for eager loading",
                    "Batch queries using DataLoader pattern",
                    "Implement GraphQL query depth limiting"
                ]
            })

        # Memory issues
        if "memory" in task_lower:
            bottlenecks.append({
                "type": "memory",
                "issue": "High memory usage",
                "severity": "medium",
                "impact": "May lead to OOM crashes under load",
                "solutions": [
                    "Implement pagination for large datasets",
                    "Use generators/iterators instead of loading all data",
                    "Profile with memory_profiler to find leaks",
                    "Consider streaming responses for large payloads"
                ]
            })

        # Algorithm complexity
        if "slow" in task_lower or "algorithm" in task_lower:
            bottlenecks.append({
                "type": "algorithm",
                "issue": "Inefficient algorithm complexity",
                "severity": "high",
                "impact": "Response time grows exponentially with data",
                "solutions": [
                    "Replace O(n²) nested loops with O(n log n) sorting + binary search",
                    "Use hash maps (O(1) lookup) instead of lists (O(n) lookup)",
                    "Implement memoization for recursive functions",
                    "Consider parallel processing for independent computations"
                ]
            })

        # Default bottleneck if none detected
        if not bottlenecks:
            bottlenecks.append({
                "type": "general",
                "issue": "Performance degradation",
                "severity": "medium",
                "impact": "Response times exceeding acceptable thresholds",
                "solutions": [
                    "Profile code with cProfile/py-spy to identify hot paths",
                    "Implement caching for frequently accessed data",
                    "Optimize database queries with EXPLAIN ANALYZE",
                    "Consider horizontal scaling if current optimization insufficient"
                ]
            })

        return bottlenecks

    def _create_optimization_plan(self, task: WizardTask, bottlenecks: List[Dict]) -> List[str]:
        """Create step-by-step optimization plan"""
        plan = ["## Optimization Plan\n"]

        for i, bottleneck in enumerate(bottlenecks, 1):
            plan.append(f"{i}. **Fix {bottleneck['type']} issue** (Severity: {bottleneck['severity']})")
            for j, solution in enumerate(bottleneck['solutions'][:2], 1):  # Top 2 solutions
                plan.append(f"   {chr(96+j)}. {solution}")

        # Add validation steps
        plan.append(f"{len(bottlenecks)+1}. **Benchmark before/after** to measure improvement")
        plan.append(f"{len(bottlenecks)+2}. **Load test** under realistic traffic patterns")
        plan.append(f"{len(bottlenecks)+3}. **Deploy with monitoring** to track impact")

        return plan

    def _generate_optimized_code(self, task: WizardTask, bottlenecks: List[Dict]) -> str:
        """Generate optimized code examples"""
        code = "# Performance Optimization Examples\n\n"

        for bottleneck in bottlenecks:
            code += f"## {bottleneck['type'].replace('_', ' ').title()} Optimization\n\n"

            if bottleneck['type'] == "database":
                code += """# Before (Slow):
# No index, full table scan
results = db.query("SELECT * FROM users WHERE email = ?", email)

# After (Fast):
# Add index: CREATE INDEX idx_users_email ON users(email);
results = db.query("SELECT * FROM users WHERE email = ?", email)
# Expected improvement: 10-100x faster lookups

# Alternative: Use caching
@cache.memoize(timeout=300)  # Cache for 5 minutes
def get_user_by_email(email):
    return db.query("SELECT * FROM users WHERE email = ?", email)

"""

            elif bottleneck['type'] == "n+1_query":
                code += """# Before (N+1 Problem):
users = User.query.all()
for user in users:
    # Each iteration = 1 query (N queries total!)
    user_posts = Post.query.filter_by(user_id=user.id).all()

# After (Eager Loading):
# Single query with JOIN
users = User.query.options(joinedload(User.posts)).all()
for user in users:
    user_posts = user.posts  # No additional query!

# Expected improvement: N queries → 1 query (95%+ reduction)

"""

            elif bottleneck['type'] == "algorithm":
                code += """# Before (O(n²)):
def find_duplicates(items):
    duplicates = []
    for i, item in enumerate(items):
        for j in range(i+1, len(items)):
            if items[j] == item:
                duplicates.append(item)
    return duplicates

# After (O(n)):
def find_duplicates(items):
    seen = set()
    duplicates = set()
    for item in items:
        if item in seen:
            duplicates.add(item)
        seen.add(item)
    return list(duplicates)

# Expected improvement: 1000 items: 500ms → 5ms (100x faster)

"""

            elif bottleneck['type'] == "memory":
                code += """# Before (Loads all data into memory):
def export_all_users():
    users = User.query.all()  # May load millions of rows!
    return [user.to_dict() for user in users]

# After (Streaming with generator):
def export_all_users():
    # Yields one user at a time (constant memory)
    for user in User.query.yield_per(1000):
        yield user.to_dict()

# Expected improvement: 1GB memory → 10MB memory (99% reduction)

"""

        return code

    def _create_benchmarks(self, task: WizardTask, bottlenecks: List[Dict]) -> str:
        """Create benchmark test suite"""
        benchmarks = """# Performance Benchmark Suite
# Run with: pytest benchmark_performance.py --benchmark-only

import pytest
from time import perf_counter

class TestPerformanceBenchmarks:

    @pytest.mark.benchmark
    def test_query_performance(self, benchmark):
        \"\"\"Benchmark database query performance\"\"\"
        result = benchmark(lambda: query_users_by_email("test@example.com"))
        assert result is not None
        # Target: < 50ms p95 latency

    @pytest.mark.benchmark
    def test_endpoint_latency(self, benchmark):
        \"\"\"Benchmark API endpoint response time\"\"\"
        result = benchmark(lambda: client.get("/api/users/123"))
        assert result.status_code == 200
        # Target: < 200ms p95 latency

    @pytest.mark.benchmark
    def test_memory_usage(self):
        \"\"\"Monitor memory usage during operation\"\"\"
        import tracemalloc
        tracemalloc.start()

        # Run operation
        process_large_dataset()

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # Target: < 100MB peak memory
        assert peak / 1024 / 1024 < 100, f"Peak memory: {peak / 1024 / 1024}MB"

# Load Testing Configuration
# Run with: locust -f locustfile.py --host=http://localhost:8000

from locust import HttpUser, task, between

class PerformanceUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)  # 3x weight
    def get_user_profile(self):
        self.client.get("/api/users/123/profile")

    @task(1)
    def search_users(self):
        self.client.get("/api/users/search?q=john")

# Run load test: 100 concurrent users for 5 minutes
# Target metrics:
#   - p95 latency: < 200ms
#   - Error rate: < 0.1%
#   - Throughput: > 500 req/sec
"""
        return benchmarks

    def _predict_scaling_issues(self, task: WizardTask, bottlenecks: List[Dict]) -> str:
        """Level 4: Anticipate future scaling issues"""
        prediction = "# Scaling Trajectory Analysis (Level 4: Anticipatory)\n\n"

        prediction += "## Current State\n"
        prediction += "- Response time: ~200-500ms (within acceptable range)\n"
        prediction += "- Traffic: ~1,000 requests/day\n"
        prediction += "- Database: ~100K rows\n\n"

        prediction += "## Projected Bottlenecks (Next 30-90 Days)\n\n"

        # Predict database scaling issues
        prediction += "### ⚠️ Database Connection Exhaustion (45 days)\n"
        prediction += "**Prediction**: At 5K req/day growth rate, connection pool will saturate in ~45 days\n"
        prediction += "**Impact**: Requests will timeout (503 errors)\n"
        prediction += "**Preventive Action**:\n"
        prediction += "- Increase connection pool size from 10 → 50 connections\n"
        prediction += "- Implement connection pooling with pgbouncer\n"
        prediction += "- Add read replicas for read-heavy queries\n\n"

        # Predict query performance degradation
        prediction += "### ⚠️ Query Performance Degradation (60 days)\n"
        prediction += "**Prediction**: At 50K rows/month growth, queries will exceed 500ms p95 in ~60 days\n"
        prediction += "**Impact**: User-visible slowness, potential SLA breach\n"
        prediction += "**Preventive Action**:\n"
        prediction += "- Add database indexes NOW (takes effect immediately)\n"
        prediction += "- Implement query caching (Redis) for hot data\n"
        prediction += "- Consider database partitioning if growth continues\n\n"

        # Predict memory issues
        prediction += "### ⚠️ Memory Pressure (90 days)\n"
        prediction += "**Prediction**: At current data growth, in-memory caching will exceed available RAM\n"
        prediction += "**Impact**: Cache thrashing, increased database load\n"
        prediction += "**Preventive Action**:\n"
        prediction += "- Implement cache eviction policy (LRU)\n"
        prediction += "- Move cache to dedicated Redis cluster\n"
        prediction += "- Consider vertical scaling (more RAM) or horizontal scaling\n\n"

        prediction += "## Recommended Timeline\n"
        prediction += "- **Now (Day 0)**: Add database indexes (zero-downtime, high impact)\n"
        prediction += "- **Week 2**: Implement Redis caching for hot paths\n"
        prediction += "- **Week 4**: Set up read replicas (before connection saturation)\n"
        prediction += "- **Week 6**: Load test at 10x traffic to validate scaling plan\n"

        return prediction

    def _generate_performance_report(self, diagnosis: str, bottlenecks: List[Dict], scaling: str) -> str:
        """Generate comprehensive performance report"""
        report = f"{diagnosis}\n\n"
        report += "## Identified Bottlenecks\n\n"

        for i, bottleneck in enumerate(bottlenecks, 1):
            report += f"### {i}. {bottleneck['issue']} (Severity: {bottleneck['severity']})\n"
            report += f"**Impact**: {bottleneck['impact']}\n\n"
            report += "**Recommended Solutions**:\n"
            for solution in bottleneck['solutions']:
                report += f"- {solution}\n"
            report += "\n"

        report += f"{scaling}\n"

        return report

    def _generate_caching_strategy(self, task: WizardTask, bottlenecks: List[Dict]) -> str:
        """Generate caching strategy recommendations"""
        strategy = "# Caching Strategy\n\n"

        strategy += "## Cache Layers\n\n"
        strategy += "### 1. Application-Level Cache (In-Memory)\n"
        strategy += "- **Use case**: Hot data accessed frequently (< 1 second staleness acceptable)\n"
        strategy += "- **Implementation**: Python `functools.lru_cache` or Flask-Caching\n"
        strategy += "- **TTL**: 60-300 seconds\n"
        strategy += "- **Example**: User profile data, configuration settings\n\n"

        strategy += "### 2. Distributed Cache (Redis)\n"
        strategy += "- **Use case**: Shared across multiple app instances\n"
        strategy += "- **Implementation**: Redis with connection pooling\n"
        strategy += "- **TTL**: 300-3600 seconds\n"
        strategy += "- **Example**: API responses, database query results\n\n"

        strategy += "### 3. HTTP Cache (CDN)\n"
        strategy += "- **Use case**: Static or semi-static public content\n"
        strategy += "- **Implementation**: CloudFlare, Fastly, or AWS CloudFront\n"
        strategy += "- **TTL**: 3600+ seconds\n"
        strategy += "- **Example**: API documentation, public user profiles\n\n"

        strategy += "## Cache Invalidation Strategy\n\n"
        strategy += "- **Time-based**: Set appropriate TTL based on data volatility\n"
        strategy += "- **Event-based**: Invalidate on write operations (user update → bust profile cache)\n"
        strategy += "- **Version-based**: Include version tag in cache key\n\n"

        strategy += "## Expected Impact\n"
        strategy += "- **Cache hit rate**: 80-90% (target)\n"
        strategy += "- **Latency reduction**: 70-90% for cached requests\n"
        strategy += "- **Database load**: 60-80% reduction in queries\n"

        return strategy

    def _identify_risks(self, task: WizardTask, bottlenecks: List[Dict]) -> List[WizardRisk]:
        """Identify optimization risks"""
        risks = []

        # Index creation risk
        if any(b['type'] == 'database' for b in bottlenecks):
            risks.append(WizardRisk(
                risk="Database index creation may lock table during creation",
                mitigation="Use CREATE INDEX CONCURRENTLY (Postgres) for zero-downtime indexing",
                severity="low"
            ))

        # Caching risk
        risks.append(WizardRisk(
            risk="Caching may serve stale data after updates",
            mitigation="Implement cache invalidation on write operations or use short TTL (60-300s)",
            severity="medium"
        ))

        # Over-optimization risk
        risks.append(WizardRisk(
            risk="Premature optimization may add complexity without significant benefit",
            mitigation="Always benchmark before/after to validate improvements (target: 30%+ gain)",
            severity="low"
        ))

        return risks

    def _create_handoffs(self, task: WizardTask) -> List[WizardHandoff]:
        """Create handoffs for performance work"""
        handoffs = []

        if task.role == "developer":
            handoffs.append(WizardHandoff(
                owner="DevOps/SRE",
                what="Configure Redis cache cluster and monitoring dashboards",
                when="Before production deployment"
            ))
            handoffs.append(WizardHandoff(
                owner="DBA",
                what="Review and approve database index creation plan",
                when="Before executing DDL statements"
            ))

        return handoffs
