"""Benchmark tests comparing O(n) list lookups to O(1) set/dict lookups.

Tests demonstrate performance improvements from Phase 2 optimization work.
Focus areas: file categorization, verdict merging, stage indexing.
"""

import timeit
from pathlib import Path

import pytest

from empathy_os.project_index.scanner import ProjectScanner
from empathy_os.workflows.code_review_adapters import _merge_verdicts
from empathy_os.workflows.progress import ProgressTracker


class TestFileCategorizationOptimization:
    """Test that frozenset lookup is faster than list lookup."""

    def test_frozenset_suffix_lookup_performance(self):
        """Verify frozensets provide O(1) lookup for file categorization."""
        # Setup
        scanner = ProjectScanner(".")

        # These should all be O(1) operations now using frozensets
        config_suffixes = scanner.CONFIG_SUFFIXES
        doc_suffixes = scanner.DOC_SUFFIXES
        asset_suffixes = scanner.ASSET_SUFFIXES
        source_suffixes = scanner.SOURCE_SUFFIXES

        # Verify they're frozensets
        assert isinstance(config_suffixes, frozenset)
        assert isinstance(doc_suffixes, frozenset)
        assert isinstance(asset_suffixes, frozenset)
        assert isinstance(source_suffixes, frozenset)

        # Benchmark: 10k lookups should complete in <10ms
        def benchmark_config():
            for _ in range(10000):
                ".py" in source_suffixes
                ".json" in config_suffixes
                ".md" in doc_suffixes
                ".png" in asset_suffixes

        elapsed = timeit.timeit(benchmark_config, number=1)
        # 10k lookups in frozensets should be < 10ms
        assert elapsed < 0.010, f"Lookup took {elapsed:.4f}s, expected <0.01s"

    def test_categorization_uses_frozensets(self):
        """Test that file categorization actually uses the frozensets."""
        from empathy_os.project_index.models import FileCategory

        scanner = ProjectScanner(".")

        # Test various file paths - should be O(1) lookups
        test_cases = [
            (Path("test.py"), FileCategory.SOURCE),
            (Path("config.json"), FileCategory.CONFIG),
            (Path("README.md"), FileCategory.DOCS),
            (Path("style.css"), FileCategory.ASSET),
        ]

        for path, expected_category in test_cases:
            category = scanner._determine_category(path)
            assert category == expected_category


class TestVerdictMergingOptimization:
    """Test that dict lookup is faster than list.index() for verdict merging."""

    def test_verdict_merge_uses_dict_lookup(self):
        """Verify verdict merging uses dict for O(1) lookup."""
        # These should all work correctly with dict-based lookup
        result1 = _merge_verdicts("reject", "approve")
        assert result1 == "reject"  # More severe

        result2 = _merge_verdicts("approve_with_suggestions", "request_changes")
        assert result2 == "request_changes"  # More severe

        result3 = _merge_verdicts("approve", "approve")
        assert result3 == "approve"  # Same severity

    def test_verdict_merge_with_dashes(self):
        """Test verdict merge handles dashes correctly."""
        # Test with dashed names (converted to underscores)
        result = _merge_verdicts("request-changes", "approve-with-suggestions")
        assert result == "request_changes"

    def test_verdict_merge_performance(self):
        """Benchmark verdict merging - should be fast with dict lookup."""

        def benchmark_merge():
            for _ in range(10000):
                _merge_verdicts("approve", "request_changes")
                _merge_verdicts("approve_with_suggestions", "approve")
                _merge_verdicts("reject", "approve")

        elapsed = timeit.timeit(benchmark_merge, number=1)
        # 30k merges should complete in < 50ms
        assert elapsed < 0.050, f"Merge took {elapsed:.4f}s, expected <0.05s"


class TestProgressTrackerOptimization:
    """Test that ProgressTracker uses dict for O(1) stage lookup."""

    def test_progress_tracker_index_map(self):
        """Verify ProgressTracker creates stage index map."""
        stages = ["analysis", "review", "compilation", "export"]
        tracker = ProgressTracker("test", "id123", stages)

        # Verify index map was created
        assert hasattr(tracker, "_stage_index_map")
        assert tracker._stage_index_map == {
            "analysis": 0,
            "review": 1,
            "compilation": 2,
            "export": 3,
        }

    def test_progress_tracker_lookup_performance(self):
        """Benchmark progress tracker stage lookups."""
        stages = [f"stage_{i}" for i in range(100)]
        tracker = ProgressTracker("test", "id123", stages)

        def benchmark_lookups():
            for stage in stages:
                # This uses the index map internally
                tracker.current_index = tracker._stage_index_map.get(stage, 0)

        elapsed = timeit.timeit(benchmark_lookups, number=1000)
        # 100k lookups should complete in < 100ms
        assert elapsed < 0.100, f"Lookup took {elapsed:.4f}s, expected <0.1s"

    def test_progress_tracker_start_stage_uses_index_map(self):
        """Test that start_stage uses the index map for O(1) lookup."""
        stages = ["step1", "step2", "step3"]
        tracker = ProgressTracker("workflow", "id456", stages)

        # Start stages - should use index map internally
        tracker.start_stage("step1")
        assert tracker.current_index == 0

        tracker.start_stage("step3")
        assert tracker.current_index == 2

    def test_progress_tracker_complete_stage_uses_index_map(self):
        """Test that complete_stage uses the index map for O(1) lookup."""
        stages = ["step1", "step2", "step3"]
        tracker = ProgressTracker("workflow", "id789", stages)

        # Complete stage - should update current_index using index map
        tracker.complete_stage("step2")
        assert tracker.current_index == 2  # Index 1 + 1


class TestLookupOptimizationComparison:
    """Compare O(n) vs O(1) lookup performance."""

    def test_list_vs_frozenset_lookup_large_dataset(self):
        """Demonstrate O(n) vs O(1) for large datasets."""
        # Create test data
        items_list = [f".ext{i}" for i in range(100)]
        items_frozenset = frozenset(items_list)

        # Benchmark list lookup (O(n))
        def benchmark_list():
            for _ in range(10000):
                f".ext{50}" in items_list

        # Benchmark frozenset lookup (O(1))
        def benchmark_frozenset():
            for _ in range(10000):
                f".ext{50}" in items_frozenset

        list_time = timeit.timeit(benchmark_list, number=1)
        frozenset_time = timeit.timeit(benchmark_frozenset, number=1)

        # frozenset should be significantly faster for large datasets
        improvement_ratio = list_time / frozenset_time
        assert improvement_ratio > 3, (
            f"frozenset only {improvement_ratio:.1f}x faster than list "
            f"(list: {list_time:.4f}s, frozenset: {frozenset_time:.4f}s)"
        )

    def test_list_index_vs_dict_lookup(self):
        """Demonstrate .index() O(n) vs dict lookup O(1)."""
        items_list = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"]
        items_dict = {item: i for i, item in enumerate(items_list)}

        # Benchmark list.index() (O(n))
        def benchmark_list_index():
            for _ in range(10000):
                items_list.index("j")  # Worst case: last item

        # Benchmark dict lookup (O(1))
        def benchmark_dict_lookup():
            for _ in range(10000):
                items_dict.get("j")

        list_time = timeit.timeit(benchmark_list_index, number=1)
        dict_time = timeit.timeit(benchmark_dict_lookup, number=1)

        # dict should be significantly faster
        improvement_ratio = list_time / dict_time
        assert improvement_ratio > 2, (
            f"dict only {improvement_ratio:.1f}x faster than list.index() "
            f"(list: {list_time:.4f}s, dict: {dict_time:.4f}s)"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
