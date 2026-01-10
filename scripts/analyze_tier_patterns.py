#!/usr/bin/env python3
"""
Analyze tier progression patterns from enhanced bug tracking.

This script demonstrates the value of tracking cascading tier retry data:
- Learn optimal starting tiers for different bug types
- Calculate actual cost savings
- Identify quality gate effectiveness
- Generate tier recommendations for new bugs

Usage:
    python scripts/analyze_tier_patterns.py
    python scripts/analyze_tier_patterns.py --bug-type integration_error
    python scripts/analyze_tier_patterns.py --recommend "integration test failure"
"""

import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


@dataclass
class TierRecommendation:
    """Recommendation for which tier to start with."""

    recommended_tier: str
    confidence: float
    reasoning: str
    historical_success_rate: float
    avg_cost: float
    avg_attempts: float


class TierPatternAnalyzer:
    """Analyze patterns from enhanced tier progression tracking."""

    def __init__(self, patterns_dir: Path = Path("patterns/debugging")):
        self.patterns_dir = patterns_dir
        self.patterns = self._load_patterns()

    def _load_patterns(self) -> list[dict]:
        """Load all patterns with tier_progression data."""
        patterns = []

        for file_path in self.patterns_dir.glob("*.json"):
            with open(file_path) as f:
                data = json.load(f)

                # Check if this is an enhanced pattern (has tier_progression)
                if isinstance(data, dict) and "tier_progression" in data:
                    patterns.append(data)
                # Or if it's a patterns array
                elif isinstance(data, dict) and "patterns" in data:
                    for pattern in data["patterns"]:
                        if "tier_progression" in pattern:
                            patterns.append(pattern)

        return patterns

    def analyze_by_bug_type(self, bug_type: str | None = None) -> dict:
        """Analyze tier success rates by bug type."""

        filtered = self.patterns
        if bug_type:
            filtered = [p for p in self.patterns if p["bug_type"] == bug_type]

        if not filtered:
            return {"error": f"No patterns found for bug_type: {bug_type}"}

        analysis = {
            "bug_type": bug_type or "all",
            "total_patterns": len(filtered),
            "tier_distribution": defaultdict(int),
            "avg_cost": 0.0,
            "avg_attempts": 0.0,
            "total_savings_percent": 0.0,
            "quality_gate_effectiveness": defaultdict(int),
        }

        total_cost = 0.0
        total_attempts = 0
        total_savings = 0.0

        for pattern in filtered:
            tp = pattern["tier_progression"]

            # Track which tier succeeded
            successful_tier = tp["successful_tier"]
            analysis["tier_distribution"][successful_tier] += 1

            # Accumulate costs
            cb = tp["cost_breakdown"]
            total_cost += cb["total_cost"]
            total_attempts += tp["total_attempts"]
            total_savings += cb["savings_percent"]

            # Track quality gate failures
            for tier_history in tp["tier_history"]:
                for failure in tier_history.get("failures", []):
                    gate = failure["quality_gate_failed"]
                    analysis["quality_gate_effectiveness"][gate] += 1

        # Calculate averages
        count = len(filtered)
        analysis["avg_cost"] = total_cost / count
        analysis["avg_attempts"] = total_attempts / count
        analysis["total_savings_percent"] = total_savings / count

        return analysis

    def recommend_tier(self, bug_description: str) -> TierRecommendation:
        """Recommend starting tier based on historical patterns."""

        # Simple keyword matching (would be ML in production)
        keywords_by_type = {
            "integration_error": ["integration", "import", "module", "package"],
            "type_mismatch": ["type", "annotation", "mypy", "typing"],
            "import_error": ["import", "module", "cannot import"],
            "unknown": [],
        }

        # Match bug type
        matched_type = "unknown"
        desc_lower = bug_description.lower()
        for bug_type, keywords in keywords_by_type.items():
            if any(kw in desc_lower for kw in keywords):
                matched_type = bug_type
                break

        # Find similar patterns
        similar = [p for p in self.patterns if p["bug_type"] == matched_type]

        if not similar:
            return TierRecommendation(
                recommended_tier="CHEAP",
                confidence=0.5,
                reasoning="No historical data, defaulting to CHEAP tier",
                historical_success_rate=0.0,
                avg_cost=0.030,
                avg_attempts=1.0,
            )

        # Calculate tier success rates
        tier_counts = defaultdict(int)
        for pattern in similar:
            tier_counts[pattern["tier_progression"]["successful_tier"]] += 1

        total = len(similar)
        success_rates = {tier: count / total for tier, count in tier_counts.items()}

        # Recommend tier with highest success rate
        recommended = max(success_rates.items(), key=lambda x: x[1])
        tier, rate = recommended

        # Calculate average cost for this tier
        avg_cost = (
            sum(
                p["tier_progression"]["cost_breakdown"]["total_cost"]
                for p in similar
                if p["tier_progression"]["successful_tier"] == tier
            )
            / tier_counts[tier]
        )

        # Calculate average attempts
        avg_attempts = (
            sum(
                p["tier_progression"]["total_attempts"]
                for p in similar
                if p["tier_progression"]["successful_tier"] == tier
            )
            / tier_counts[tier]
        )

        return TierRecommendation(
            recommended_tier=tier,
            confidence=rate,
            reasoning=f"{int(rate * 100)}% of similar bugs ({matched_type}) resolved at {tier} tier",
            historical_success_rate=rate,
            avg_cost=avg_cost,
            avg_attempts=avg_attempts,
        )

    def calculate_savings(self) -> dict:
        """Calculate total savings from cascading tier approach."""

        if not self.patterns:
            return {"error": "No patterns with tier data found"}

        total_cost = 0.0
        potential_cost = 0.0

        for pattern in self.patterns:
            cb = pattern["tier_progression"]["cost_breakdown"]
            total_cost += cb["total_cost"]
            potential_cost += cb["cost_if_always_premium"]

        savings_percent = ((potential_cost - total_cost) / potential_cost) * 100

        return {
            "total_patterns": len(self.patterns),
            "actual_cost": round(total_cost, 2),
            "cost_if_always_premium": round(potential_cost, 2),
            "total_savings": round(potential_cost - total_cost, 2),
            "savings_percent": round(savings_percent, 1),
            "cost_per_bug": round(total_cost / len(self.patterns), 3),
        }

    def quality_gate_report(self) -> dict:
        """Analyze which quality gates catch the most issues."""

        gate_failures = defaultdict(int)
        total_failures = 0

        for pattern in self.patterns:
            for tier_history in pattern["tier_progression"]["tier_history"]:
                for failure in tier_history.get("failures", []):
                    gate = failure["quality_gate_failed"]
                    gate_failures[gate] += 1
                    total_failures += 1

        if total_failures == 0:
            return {"message": "No failures in current patterns (all succeeded on first attempt)"}

        # Sort by frequency
        sorted_gates = sorted(gate_failures.items(), key=lambda x: x[1], reverse=True)

        return {
            "total_failures": total_failures,
            "gate_effectiveness": [
                {
                    "gate": gate,
                    "failures_caught": count,
                    "percent": round((count / total_failures) * 100, 1),
                }
                for gate, count in sorted_gates
            ],
        }

    def xml_protocol_effectiveness(self) -> dict:
        """Analyze XML protocol compliance and effectiveness."""

        if not self.patterns:
            return {"error": "No patterns found"}

        xml_patterns = [
            p for p in self.patterns if "xml_protocol_compliance" in p["tier_progression"]
        ]

        if not xml_patterns:
            return {"message": "No XML protocol data in patterns"}

        total = len(xml_patterns)
        compliance_metrics = {
            "total_analyzed": total,
            "prompt_used_xml": 0,
            "response_used_xml": 0,
            "all_sections_present": 0,
            "test_evidence_provided": 0,
            "false_complete_avoided": 0,
        }

        for pattern in xml_patterns:
            xpc = pattern["tier_progression"]["xml_protocol_compliance"]
            for key in compliance_metrics:
                if key != "total_analyzed" and xpc.get(key):
                    compliance_metrics[key] += 1

        # Calculate percentages
        percent_keys = []
        for key in list(compliance_metrics.keys()):
            if key != "total_analyzed":
                count = compliance_metrics[key]
                percent_keys.append((f"{key}_percent", round((count / total) * 100, 1)))

        for key, value in percent_keys:
            compliance_metrics[key] = value

        return compliance_metrics


def main():
    """Run analysis and display results."""
    import argparse

    parser = argparse.ArgumentParser(description="Analyze tier progression patterns")
    parser.add_argument("--bug-type", help="Filter by specific bug type", default=None)
    parser.add_argument(
        "--recommend", help="Get tier recommendation for bug description", default=None
    )
    args = parser.parse_args()

    analyzer = TierPatternAnalyzer()

    print("\n" + "=" * 60)
    print("TIER PROGRESSION PATTERN ANALYSIS")
    print("=" * 60 + "\n")

    # 1. Cost Savings Analysis
    print("📊 COST SAVINGS ANALYSIS")
    print("-" * 60)
    savings = analyzer.calculate_savings()
    if "error" in savings:
        print(f"⚠️  {savings['error']}")
    else:
        print(f"Total patterns analyzed: {savings['total_patterns']}")
        print(f"Actual cost (cascading): ${savings['actual_cost']}")
        print(f"Cost if always PREMIUM: ${savings['cost_if_always_premium']}")
        print(f"Total savings: ${savings['total_savings']}")
        print(f"Savings percentage: {savings['savings_percent']}%")
        print(f"Average cost per bug: ${savings['cost_per_bug']}")

    # 2. Bug Type Analysis
    print("\n\n🔍 BUG TYPE ANALYSIS")
    print("-" * 60)
    analysis = analyzer.analyze_by_bug_type(args.bug_type)
    if "error" in analysis:
        print(f"⚠️  {analysis['error']}")
    else:
        print(f"Bug type: {analysis['bug_type']}")
        print(f"Total patterns: {analysis['total_patterns']}")
        print("\nTier Distribution:")
        for tier, count in analysis["tier_distribution"].items():
            percent = (count / analysis["total_patterns"]) * 100
            print(f"  {tier}: {count} ({percent:.1f}%)")
        print(f"\nAverage cost: ${analysis['avg_cost']:.3f}")
        print(f"Average attempts: {analysis['avg_attempts']:.1f}")
        print(f"Average savings: {analysis['total_savings_percent']:.1f}%")

    # 3. Quality Gate Effectiveness
    print("\n\n🛡️  QUALITY GATE EFFECTIVENESS")
    print("-" * 60)
    gate_report = analyzer.quality_gate_report()
    if "message" in gate_report:
        print(f"✅ {gate_report['message']}")
    else:
        print(f"Total failures caught: {gate_report['total_failures']}")
        print("\nGate Effectiveness:")
        for gate_data in gate_report["gate_effectiveness"]:
            print(
                f"  {gate_data['gate']}: {gate_data['failures_caught']} failures ({gate_data['percent']}%)"
            )

    # 4. XML Protocol Effectiveness
    print("\n\n📋 XML PROTOCOL EFFECTIVENESS")
    print("-" * 60)
    xml_report = analyzer.xml_protocol_effectiveness()
    if "error" in xml_report or "message" in xml_report:
        print(f"⚠️  {xml_report.get('error') or xml_report.get('message')}")
    else:
        print(f"Patterns analyzed: {xml_report['total_analyzed']}")
        print(f"Prompt used XML: {xml_report['prompt_used_xml_percent']}%")
        print(f"Response used XML: {xml_report['response_used_xml_percent']}%")
        print(f"All sections present: {xml_report['all_sections_present_percent']}%")
        print(f"Test evidence provided: {xml_report['test_evidence_provided_percent']}%")
        print(f"False completes avoided: {xml_report['false_complete_avoided_percent']}%")

    # 5. Tier Recommendation (if requested)
    if args.recommend:
        print("\n\n💡 TIER RECOMMENDATION")
        print("-" * 60)
        rec = analyzer.recommend_tier(args.recommend)
        print(f"Bug description: {args.recommend}")
        print(f"\nRecommendation: Start with {rec.recommended_tier} tier")
        print(f"Confidence: {rec.confidence * 100:.1f}%")
        print(f"Reasoning: {rec.reasoning}")
        print(f"Historical success rate: {rec.historical_success_rate * 100:.1f}%")
        print(f"Expected cost: ${rec.avg_cost:.3f}")
        print(f"Expected attempts: {rec.avg_attempts:.1f}")

    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    main()
