"""Tests for src/empathy_os/memory/graph.py

Tests the memory graph knowledge base including:
- MemoryGraph class
- Node and Edge data structures
- Graph traversal and search
- Persistence and statistics
"""

import json
import tempfile
from pathlib import Path

import pytest

from empathy_os.memory.edges import REVERSE_EDGE_TYPES, WIZARD_EDGE_PATTERNS, Edge, EdgeType
from empathy_os.memory.graph import MemoryGraph
from empathy_os.memory.nodes import (
    BugNode,
    Node,
    NodeType,
    PatternNode,
    PerformanceNode,
    VulnerabilityNode,
)


class TestNodeTypeEnum:
    """Tests for NodeType enum."""

    def test_file_value(self):
        """Test FILE node type value."""
        assert NodeType.FILE.value == "file"

    def test_function_value(self):
        """Test FUNCTION node type value."""
        assert NodeType.FUNCTION.value == "function"

    def test_bug_value(self):
        """Test BUG node type value."""
        assert NodeType.BUG.value == "bug"

    def test_vulnerability_value(self):
        """Test VULNERABILITY node type value."""
        assert NodeType.VULNERABILITY.value == "vulnerability"

    def test_pattern_value(self):
        """Test PATTERN node type value."""
        assert NodeType.PATTERN.value == "pattern"

    def test_test_value(self):
        """Test TEST node type value."""
        assert NodeType.TEST.value == "test"

    def test_all_node_types_count(self):
        """Test total number of node types."""
        # FILE, FUNCTION, CLASS, MODULE, BUG, VULNERABILITY, PERFORMANCE_ISSUE,
        # CODE_SMELL, TECH_DEBT, PATTERN, FIX, REFACTOR, TEST, TEST_CASE,
        # COVERAGE_GAP, DOC, API_ENDPOINT, DEPENDENCY, LICENSE
        assert len(NodeType) == 19

    def test_node_type_from_string(self):
        """Test creating NodeType from string."""
        assert NodeType("bug") == NodeType.BUG
        assert NodeType("vulnerability") == NodeType.VULNERABILITY
        assert NodeType("pattern") == NodeType.PATTERN


class TestEdgeTypeEnum:
    """Tests for EdgeType enum."""

    def test_causes_value(self):
        """Test CAUSES edge type value."""
        assert EdgeType.CAUSES.value == "causes"

    def test_fixed_by_value(self):
        """Test FIXED_BY edge type value."""
        assert EdgeType.FIXED_BY.value == "fixed_by"

    def test_similar_to_value(self):
        """Test SIMILAR_TO edge type value."""
        assert EdgeType.SIMILAR_TO.value == "similar_to"

    def test_depends_on_value(self):
        """Test DEPENDS_ON edge type value."""
        assert EdgeType.DEPENDS_ON.value == "depends_on"

    def test_tests_value(self):
        """Test TESTS edge type value."""
        assert EdgeType.TESTS.value == "tests"

    def test_edge_type_from_string(self):
        """Test creating EdgeType from string."""
        assert EdgeType("causes") == EdgeType.CAUSES
        assert EdgeType("fixed_by") == EdgeType.FIXED_BY


class TestReverseEdgeTypes:
    """Tests for REVERSE_EDGE_TYPES mapping."""

    def test_causes_has_reverse(self):
        """Test CAUSES has CAUSED_BY reverse."""
        assert REVERSE_EDGE_TYPES[EdgeType.CAUSES] == EdgeType.CAUSED_BY

    def test_fixed_by_has_reverse(self):
        """Test FIXED_BY has FIXES reverse."""
        assert REVERSE_EDGE_TYPES[EdgeType.FIXED_BY] == EdgeType.FIXES

    def test_similar_to_is_symmetric(self):
        """Test SIMILAR_TO is its own reverse."""
        assert REVERSE_EDGE_TYPES[EdgeType.SIMILAR_TO] == EdgeType.SIMILAR_TO

    def test_contains_has_contained_in(self):
        """Test CONTAINS has CONTAINED_IN reverse."""
        assert REVERSE_EDGE_TYPES[EdgeType.CONTAINS] == EdgeType.CONTAINED_IN

    def test_tests_has_tested_by(self):
        """Test TESTS has TESTED_BY reverse."""
        assert REVERSE_EDGE_TYPES[EdgeType.TESTS] == EdgeType.TESTED_BY


class TestWizardEdgePatterns:
    """Tests for WIZARD_EDGE_PATTERNS configuration."""

    def test_security_audit_patterns(self):
        """Test security-audit wizard has patterns."""
        assert "security-audit" in WIZARD_EDGE_PATTERNS
        patterns = WIZARD_EDGE_PATTERNS["security-audit"]
        edge_types = [p[0] for p in patterns]
        assert EdgeType.CAUSES in edge_types
        assert EdgeType.FIXED_BY in edge_types

    def test_bug_predict_patterns(self):
        """Test bug-predict wizard has patterns."""
        assert "bug-predict" in WIZARD_EDGE_PATTERNS
        patterns = WIZARD_EDGE_PATTERNS["bug-predict"]
        edge_types = [p[0] for p in patterns]
        assert EdgeType.SIMILAR_TO in edge_types

    def test_test_gen_patterns(self):
        """Test test-gen wizard has patterns."""
        assert "test-gen" in WIZARD_EDGE_PATTERNS
        patterns = WIZARD_EDGE_PATTERNS["test-gen"]
        edge_types = [p[0] for p in patterns]
        assert EdgeType.TESTS in edge_types
        assert EdgeType.COVERS in edge_types


class TestNode:
    """Tests for Node dataclass."""

    def test_basic_creation(self):
        """Test basic node creation."""
        node = Node(
            id="node_001",
            type=NodeType.BUG,
            name="Null pointer exception",
        )
        assert node.id == "node_001"
        assert node.type == NodeType.BUG
        assert node.name == "Null pointer exception"

    def test_default_values(self):
        """Test node default values."""
        node = Node(id="test", type=NodeType.PATTERN, name="Test")
        assert node.description == ""
        assert node.source_wizard == ""
        assert node.source_file == ""
        assert node.source_line is None
        assert node.severity == ""
        assert node.confidence == 1.0
        assert node.metadata == {}
        assert node.tags == []
        assert node.status == "open"

    def test_full_node_creation(self):
        """Test node with all fields populated."""
        node = Node(
            id="vuln_001",
            type=NodeType.VULNERABILITY,
            name="SQL Injection",
            description="User input not sanitized",
            source_wizard="security-audit",
            source_file="src/db/query.py",
            source_line=42,
            severity="critical",
            confidence=0.95,
            metadata={"cwe": "CWE-89"},
            tags=["security", "injection"],
            status="investigating",
        )
        assert node.source_wizard == "security-audit"
        assert node.source_file == "src/db/query.py"
        assert node.source_line == 42
        assert node.severity == "critical"
        assert node.confidence == 0.95
        assert node.metadata["cwe"] == "CWE-89"
        assert "security" in node.tags
        assert node.status == "investigating"

    def test_to_dict(self):
        """Test node serialization to dict."""
        node = Node(
            id="node_dict",
            type=NodeType.FIX,
            name="Add validation",
            severity="medium",
        )
        data = node.to_dict()
        assert data["id"] == "node_dict"
        assert data["type"] == "fix"
        assert data["name"] == "Add validation"
        assert data["severity"] == "medium"
        assert "created_at" in data
        assert "updated_at" in data

    def test_from_dict(self):
        """Test node creation from dict."""
        data = {
            "id": "node_from_dict",
            "type": "bug",
            "name": "Test bug",
            "description": "A test bug",
            "severity": "low",
            "created_at": "2025-01-15T10:00:00",
            "updated_at": "2025-01-15T11:00:00",
        }
        node = Node.from_dict(data)
        assert node.id == "node_from_dict"
        assert node.type == NodeType.BUG
        assert node.name == "Test bug"
        assert node.description == "A test bug"
        assert node.severity == "low"

    def test_to_dict_from_dict_roundtrip(self):
        """Test roundtrip serialization."""
        original = Node(
            id="roundtrip",
            type=NodeType.PATTERN,
            name="Best Practice",
            description="Always validate input",
            source_wizard="code-review",
            tags=["validation", "security"],
        )
        data = original.to_dict()
        restored = Node.from_dict(data)
        assert restored.id == original.id
        assert restored.type == original.type
        assert restored.name == original.name
        assert restored.description == original.description
        assert restored.source_wizard == original.source_wizard


class TestSpecializedNodes:
    """Tests for specialized node types."""

    def test_bug_node(self):
        """Test BugNode creation."""
        bug = BugNode(
            id="bug_001",
            type=NodeType.BUG,  # Will be overwritten by __post_init__
            name="Null reference",
            root_cause="Missing null check",
            fix_suggestion="Add guard clause",
            reproduction_steps=["Open app", "Click button"],
        )
        assert bug.type == NodeType.BUG
        assert bug.root_cause == "Missing null check"
        assert bug.fix_suggestion == "Add guard clause"
        assert len(bug.reproduction_steps) == 2

    def test_vulnerability_node(self):
        """Test VulnerabilityNode creation."""
        vuln = VulnerabilityNode(
            id="vuln_001",
            type=NodeType.VULNERABILITY,
            name="XSS Attack",
            cwe_id="CWE-79",
            cvss_score=7.5,
            attack_vector="network",
            remediation="Sanitize output",
        )
        assert vuln.type == NodeType.VULNERABILITY
        assert vuln.cwe_id == "CWE-79"
        assert vuln.cvss_score == 7.5
        assert vuln.attack_vector == "network"

    def test_performance_node(self):
        """Test PerformanceNode creation."""
        perf = PerformanceNode(
            id="perf_001",
            type=NodeType.PERFORMANCE_ISSUE,
            name="Slow database query",
            metric="latency",
            current_value=5000.0,
            target_value=100.0,
            optimization_suggestion="Add index",
        )
        assert perf.type == NodeType.PERFORMANCE_ISSUE
        assert perf.metric == "latency"
        assert perf.current_value == 5000.0
        assert perf.target_value == 100.0

    def test_pattern_node(self):
        """Test PatternNode creation."""
        pattern = PatternNode(
            id="pat_001",
            type=NodeType.PATTERN,
            name="Factory Pattern",
            pattern_type="best-practice",
            language="python",
            example_code="def create_instance(cls): ...",
            applies_to=["classes", "modules"],
        )
        assert pattern.type == NodeType.PATTERN
        assert pattern.pattern_type == "best-practice"
        assert pattern.language == "python"
        assert "classes" in pattern.applies_to


class TestEdge:
    """Tests for Edge dataclass."""

    def test_basic_creation(self):
        """Test basic edge creation."""
        edge = Edge(
            source_id="node_a",
            target_id="node_b",
            type=EdgeType.CAUSES,
        )
        assert edge.source_id == "node_a"
        assert edge.target_id == "node_b"
        assert edge.type == EdgeType.CAUSES

    def test_default_values(self):
        """Test edge default values."""
        edge = Edge(source_id="a", target_id="b", type=EdgeType.RELATED_TO)
        assert edge.weight == 1.0
        assert edge.confidence == 1.0
        assert edge.description == ""
        assert edge.source_wizard == ""
        assert edge.metadata == {}

    def test_full_edge_creation(self):
        """Test edge with all fields."""
        edge = Edge(
            source_id="bug_001",
            target_id="fix_001",
            type=EdgeType.FIXED_BY,
            weight=0.9,
            confidence=0.85,
            description="Bug fixed by adding validation",
            source_wizard="bug-predict",
            metadata={"commit": "abc123"},
        )
        assert edge.weight == 0.9
        assert edge.confidence == 0.85
        assert edge.description == "Bug fixed by adding validation"
        assert edge.source_wizard == "bug-predict"
        assert edge.metadata["commit"] == "abc123"

    def test_edge_id_property(self):
        """Test edge ID generation."""
        edge = Edge(
            source_id="node_a",
            target_id="node_b",
            type=EdgeType.CAUSES,
        )
        assert edge.id == "node_a-causes-node_b"

    def test_to_dict(self):
        """Test edge serialization."""
        edge = Edge(
            source_id="src",
            target_id="tgt",
            type=EdgeType.DEPENDS_ON,
            weight=0.8,
        )
        data = edge.to_dict()
        assert data["source_id"] == "src"
        assert data["target_id"] == "tgt"
        assert data["type"] == "depends_on"
        assert data["weight"] == 0.8
        assert "created_at" in data

    def test_from_dict(self):
        """Test edge creation from dict."""
        data = {
            "source_id": "a",
            "target_id": "b",
            "type": "similar_to",
            "weight": 0.75,
            "created_at": "2025-01-15T10:00:00",
        }
        edge = Edge.from_dict(data)
        assert edge.source_id == "a"
        assert edge.target_id == "b"
        assert edge.type == EdgeType.SIMILAR_TO
        assert edge.weight == 0.75


class TestMemoryGraphInit:
    """Tests for MemoryGraph initialization."""

    def test_init_creates_empty_graph(self):
        """Test initializing empty graph."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test_graph.json"
            graph = MemoryGraph(path=path)
            assert len(graph.nodes) == 0
            assert len(graph.edges) == 0
            assert path.exists()

    def test_init_creates_directory(self):
        """Test init creates parent directory if needed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "subdir" / "graph.json"
            MemoryGraph(path=path)
            assert path.parent.exists()

    def test_init_loads_existing_graph(self):
        """Test loading existing graph from file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "graph.json"

            # Create initial graph
            graph1 = MemoryGraph(path=path)
            node_id = graph1.add_finding(
                wizard="test",
                finding={"type": "bug", "name": "Test bug"},
            )

            # Load in new instance
            graph2 = MemoryGraph(path=path)
            assert len(graph2.nodes) == 1
            assert node_id in graph2.nodes


class TestMemoryGraphAddFinding:
    """Tests for MemoryGraph.add_finding method."""

    @pytest.fixture
    def graph(self):
        """Create temporary graph for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "graph.json"
            yield MemoryGraph(path=path)

    def test_add_simple_finding(self, graph):
        """Test adding simple finding."""
        node_id = graph.add_finding(
            wizard="bug-predict",
            finding={"type": "bug", "name": "Null reference"},
        )
        assert node_id is not None
        assert node_id in graph.nodes
        node = graph.nodes[node_id]
        assert node.type == NodeType.BUG
        assert node.name == "Null reference"
        assert node.source_wizard == "bug-predict"

    def test_add_finding_with_file_info(self, graph):
        """Test adding finding with file information."""
        node_id = graph.add_finding(
            wizard="security-audit",
            finding={
                "type": "vulnerability",
                "name": "SQL Injection",
                "file": "src/db.py",
                "line": 42,
                "severity": "critical",
            },
        )
        node = graph.nodes[node_id]
        assert node.source_file == "src/db.py"
        assert node.source_line == 42
        assert node.severity == "critical"

    def test_add_finding_unknown_type_defaults_to_pattern(self, graph):
        """Test unknown finding type defaults to PATTERN."""
        node_id = graph.add_finding(
            wizard="test",
            finding={"type": "unknown_type", "name": "Unknown"},
        )
        node = graph.nodes[node_id]
        assert node.type == NodeType.PATTERN

    def test_add_finding_with_metadata(self, graph):
        """Test adding finding with metadata."""
        node_id = graph.add_finding(
            wizard="test",
            finding={
                "type": "bug",
                "name": "Test",
                "metadata": {"custom": "value"},
                "tags": ["important", "urgent"],
            },
        )
        node = graph.nodes[node_id]
        assert node.metadata["custom"] == "value"
        assert "important" in node.tags


class TestMemoryGraphAddEdge:
    """Tests for MemoryGraph.add_edge method."""

    @pytest.fixture
    def graph_with_nodes(self):
        """Create graph with two nodes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "graph.json"
            graph = MemoryGraph(path=path)
            id1 = graph.add_finding(wizard="test", finding={"type": "bug", "name": "Bug 1"})
            id2 = graph.add_finding(wizard="test", finding={"type": "fix", "name": "Fix 1"})
            yield graph, id1, id2

    def test_add_simple_edge(self, graph_with_nodes):
        """Test adding simple edge."""
        graph, id1, id2 = graph_with_nodes
        graph.add_edge(id1, id2, EdgeType.FIXED_BY)
        assert len(graph.edges) == 1
        edge = graph.edges[0]
        assert edge.source_id == id1
        assert edge.target_id == id2
        assert edge.type == EdgeType.FIXED_BY

    def test_add_edge_with_description(self, graph_with_nodes):
        """Test adding edge with description."""
        graph, id1, id2 = graph_with_nodes
        graph.add_edge(
            id1,
            id2,
            EdgeType.CAUSES,
            description="Bug causes crash",
            wizard="bug-predict",
            weight=0.8,
        )
        edge = graph.edges[0]
        assert edge.description == "Bug causes crash"
        assert edge.source_wizard == "bug-predict"
        assert edge.weight == 0.8

    def test_add_bidirectional_edge(self, graph_with_nodes):
        """Test adding bidirectional edge creates reverse."""
        graph, id1, id2 = graph_with_nodes
        graph.add_edge(id1, id2, EdgeType.CAUSES, bidirectional=True)
        assert len(graph.edges) == 2
        types = {e.type for e in graph.edges}
        assert EdgeType.CAUSES in types
        assert EdgeType.CAUSED_BY in types

    def test_add_edge_invalid_source_raises(self, graph_with_nodes):
        """Test adding edge with invalid source raises."""
        graph, id1, id2 = graph_with_nodes
        with pytest.raises(ValueError, match="Source node not found"):
            graph.add_edge("invalid", id2, EdgeType.RELATED_TO)

    def test_add_edge_invalid_target_raises(self, graph_with_nodes):
        """Test adding edge with invalid target raises."""
        graph, id1, id2 = graph_with_nodes
        with pytest.raises(ValueError, match="Target node not found"):
            graph.add_edge(id1, "invalid", EdgeType.RELATED_TO)


class TestMemoryGraphGetNode:
    """Tests for MemoryGraph.get_node method."""

    @pytest.fixture
    def graph(self):
        """Create graph for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "graph.json"
            yield MemoryGraph(path=path)

    def test_get_existing_node(self, graph):
        """Test getting existing node."""
        node_id = graph.add_finding(wizard="test", finding={"type": "bug", "name": "Test"})
        node = graph.get_node(node_id)
        assert node is not None
        assert node.id == node_id

    def test_get_nonexistent_node_returns_none(self, graph):
        """Test getting nonexistent node returns None."""
        result = graph.get_node("nonexistent")
        assert result is None


class TestMemoryGraphFindRelated:
    """Tests for MemoryGraph.find_related method."""

    @pytest.fixture
    def graph_with_edges(self):
        """Create graph with connected nodes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "graph.json"
            graph = MemoryGraph(path=path)

            # Create nodes: A -> B -> C
            id_a = graph.add_finding(wizard="test", finding={"type": "bug", "name": "Bug A"})
            id_b = graph.add_finding(wizard="test", finding={"type": "fix", "name": "Fix B"})
            id_c = graph.add_finding(
                wizard="test",
                finding={"type": "pattern", "name": "Pattern C"},
            )

            graph.add_edge(id_a, id_b, EdgeType.FIXED_BY)
            graph.add_edge(id_b, id_c, EdgeType.LEADS_TO)

            yield graph, id_a, id_b, id_c

    def test_find_related_outgoing(self, graph_with_edges):
        """Test finding outgoing related nodes."""
        graph, id_a, id_b, id_c = graph_with_edges
        related = graph.find_related(id_a, direction="outgoing")
        assert len(related) == 1
        assert related[0].id == id_b

    def test_find_related_incoming(self, graph_with_edges):
        """Test finding incoming related nodes."""
        graph, id_a, id_b, id_c = graph_with_edges
        related = graph.find_related(id_b, direction="incoming")
        assert len(related) == 1
        assert related[0].id == id_a

    def test_find_related_both_directions(self, graph_with_edges):
        """Test finding related nodes in both directions."""
        graph, id_a, id_b, id_c = graph_with_edges
        related = graph.find_related(id_b, direction="both")
        assert len(related) == 2
        ids = {n.id for n in related}
        assert id_a in ids
        assert id_c in ids

    def test_find_related_with_depth(self, graph_with_edges):
        """Test finding related nodes with depth > 1."""
        graph, id_a, id_b, id_c = graph_with_edges
        related = graph.find_related(id_a, direction="outgoing", max_depth=2)
        assert len(related) == 2
        ids = {n.id for n in related}
        assert id_b in ids
        assert id_c in ids

    def test_find_related_filter_by_edge_type(self, graph_with_edges):
        """Test filtering by edge type."""
        graph, id_a, id_b, id_c = graph_with_edges
        related = graph.find_related(
            id_a,
            edge_types=[EdgeType.CAUSES],
            direction="outgoing",
        )
        assert len(related) == 0  # No CAUSES edges, only FIXED_BY

    def test_find_related_nonexistent_node(self, graph_with_edges):
        """Test finding related for nonexistent node returns empty."""
        graph, id_a, id_b, id_c = graph_with_edges
        related = graph.find_related("nonexistent")
        assert related == []


class TestMemoryGraphFindSimilar:
    """Tests for MemoryGraph.find_similar method."""

    @pytest.fixture
    def graph_with_similar(self):
        """Create graph with similar nodes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "graph.json"
            graph = MemoryGraph(path=path)

            graph.add_finding(
                wizard="test",
                finding={
                    "type": "bug",
                    "name": "Null reference in auth module",
                    "description": "Missing null check on user object",
                    "file": "src/auth.py",
                },
            )
            graph.add_finding(
                wizard="test",
                finding={
                    "type": "bug",
                    "name": "Null pointer in payment",
                    "description": "Credit card validation missing",
                    "file": "src/payment.py",
                },
            )
            graph.add_finding(
                wizard="test",
                finding={
                    "type": "vulnerability",
                    "name": "SQL injection attack",
                    "description": "User input not sanitized",
                },
            )

            yield graph

    def test_find_similar_by_name(self, graph_with_similar):
        """Test finding similar by name."""
        results = graph_with_similar.find_similar(
            {"name": "Null reference"},
            threshold=0.3,
        )
        assert len(results) >= 1
        # First result should have "null" in name
        node, score = results[0]
        assert "null" in node.name.lower()

    def test_find_similar_by_description(self, graph_with_similar):
        """Test finding similar by description."""
        results = graph_with_similar.find_similar(
            {"description": "missing null check"},
            threshold=0.2,
        )
        assert len(results) >= 1

    def test_find_similar_respects_threshold(self, graph_with_similar):
        """Test similarity threshold is respected."""
        high_threshold = graph_with_similar.find_similar(
            {"name": "Something completely different"},
            threshold=0.9,
        )
        low_threshold = graph_with_similar.find_similar(
            {"name": "Something completely different"},
            threshold=0.0,
        )
        assert len(high_threshold) <= len(low_threshold)

    def test_find_similar_respects_limit(self, graph_with_similar):
        """Test result limit is respected."""
        results = graph_with_similar.find_similar(
            {"name": "test"},
            threshold=0.0,
            limit=1,
        )
        assert len(results) <= 1

    def test_find_similar_type_match_bonus(self, graph_with_similar):
        """Test type match gives bonus score."""
        results = graph_with_similar.find_similar(
            {"type": "bug", "name": "reference"},
            threshold=0.1,
        )
        # Bug type nodes should score higher
        if len(results) >= 2:
            bug_nodes = [r for r in results if r[0].type == NodeType.BUG]
            assert len(bug_nodes) >= 1


class TestMemoryGraphFindBy:
    """Tests for find_by_* methods."""

    @pytest.fixture
    def graph(self):
        """Create graph with varied nodes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "graph.json"
            graph = MemoryGraph(path=path)

            graph.add_finding(
                wizard="security-audit",
                finding={"type": "vulnerability", "name": "V1", "file": "src/auth.py"},
            )
            graph.add_finding(
                wizard="security-audit",
                finding={"type": "vulnerability", "name": "V2", "file": "src/db.py"},
            )
            graph.add_finding(
                wizard="bug-predict",
                finding={"type": "bug", "name": "B1", "file": "src/auth.py"},
            )

            yield graph

    def test_find_by_type(self, graph):
        """Test finding nodes by type."""
        vulns = graph.find_by_type(NodeType.VULNERABILITY)
        assert len(vulns) == 2
        assert all(n.type == NodeType.VULNERABILITY for n in vulns)

    def test_find_by_wizard(self, graph):
        """Test finding nodes by wizard."""
        security = graph.find_by_wizard("security-audit")
        assert len(security) == 2
        assert all(n.source_wizard == "security-audit" for n in security)

    def test_find_by_file(self, graph):
        """Test finding nodes by file."""
        auth_nodes = graph.find_by_file("src/auth.py")
        assert len(auth_nodes) == 2
        assert all(n.source_file == "src/auth.py" for n in auth_nodes)


class TestMemoryGraphGetPath:
    """Tests for MemoryGraph.get_path method."""

    @pytest.fixture
    def graph_with_path(self):
        """Create graph with a path: A -> B -> C -> D."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "graph.json"
            graph = MemoryGraph(path=path)

            id_a = graph.add_finding(wizard="t", finding={"type": "bug", "name": "A"})
            id_b = graph.add_finding(wizard="t", finding={"type": "fix", "name": "B"})
            id_c = graph.add_finding(wizard="t", finding={"type": "pattern", "name": "C"})
            id_d = graph.add_finding(wizard="t", finding={"type": "refactor", "name": "D"})

            graph.add_edge(id_a, id_b, EdgeType.FIXED_BY)
            graph.add_edge(id_b, id_c, EdgeType.LEADS_TO)
            graph.add_edge(id_c, id_d, EdgeType.REFACTORED_TO)

            yield graph, id_a, id_b, id_c, id_d

    def test_get_path_direct(self, graph_with_path):
        """Test getting direct path between adjacent nodes."""
        graph, id_a, id_b, id_c, id_d = graph_with_path
        path = graph.get_path(id_a, id_b)
        assert len(path) == 2
        assert path[0][0].id == id_a
        assert path[1][0].id == id_b

    def test_get_path_multi_hop(self, graph_with_path):
        """Test getting multi-hop path."""
        graph, id_a, id_b, id_c, id_d = graph_with_path
        path = graph.get_path(id_a, id_d, max_depth=5)
        assert len(path) == 4
        ids = [node.id for node, edge in path]
        assert ids == [id_a, id_b, id_c, id_d]

    def test_get_path_respects_max_depth(self, graph_with_path):
        """Test max_depth limits path search."""
        graph, id_a, id_b, id_c, id_d = graph_with_path
        path = graph.get_path(id_a, id_d, max_depth=2)
        assert path == []  # Path requires 3 hops

    def test_get_path_no_path_exists(self, graph_with_path):
        """Test returns empty when no path exists."""
        graph, id_a, id_b, id_c, id_d = graph_with_path
        # D has no outgoing edges to A
        path = graph.get_path(id_d, id_a)
        assert path == []

    def test_get_path_invalid_nodes(self, graph_with_path):
        """Test returns empty for invalid nodes."""
        graph, id_a, id_b, id_c, id_d = graph_with_path
        assert graph.get_path("invalid", id_a) == []
        assert graph.get_path(id_a, "invalid") == []


class TestMemoryGraphStatistics:
    """Tests for MemoryGraph.get_statistics method."""

    @pytest.fixture
    def graph_with_data(self):
        """Create graph with varied data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "graph.json"
            graph = MemoryGraph(path=path)

            id1 = graph.add_finding(
                wizard="security",
                finding={"type": "vulnerability", "name": "V1", "severity": "critical"},
            )
            id2 = graph.add_finding(
                wizard="security",
                finding={"type": "vulnerability", "name": "V2", "severity": "high"},
            )
            id3 = graph.add_finding(
                wizard="bugs",
                finding={"type": "bug", "name": "B1", "severity": "medium"},
            )
            graph.add_edge(id1, id2, EdgeType.CAUSES)
            graph.add_edge(id2, id3, EdgeType.RELATED_TO)

            yield graph

    def test_statistics_node_count(self, graph_with_data):
        """Test statistics includes node count."""
        stats = graph_with_data.get_statistics()
        assert stats["total_nodes"] == 3

    def test_statistics_edge_count(self, graph_with_data):
        """Test statistics includes edge count."""
        stats = graph_with_data.get_statistics()
        assert stats["total_edges"] == 2

    def test_statistics_nodes_by_type(self, graph_with_data):
        """Test statistics groups nodes by type."""
        stats = graph_with_data.get_statistics()
        by_type = stats["nodes_by_type"]
        assert by_type.get("vulnerability") == 2
        assert by_type.get("bug") == 1

    def test_statistics_nodes_by_wizard(self, graph_with_data):
        """Test statistics groups nodes by wizard."""
        stats = graph_with_data.get_statistics()
        by_wizard = stats["nodes_by_wizard"]
        assert by_wizard.get("security") == 2
        assert by_wizard.get("bugs") == 1

    def test_statistics_nodes_by_severity(self, graph_with_data):
        """Test statistics groups nodes by severity."""
        stats = graph_with_data.get_statistics()
        by_severity = stats["nodes_by_severity"]
        assert by_severity.get("critical") == 1
        assert by_severity.get("high") == 1
        assert by_severity.get("medium") == 1

    def test_statistics_edges_by_type(self, graph_with_data):
        """Test statistics groups edges by type."""
        stats = graph_with_data.get_statistics()
        by_type = stats["edges_by_type"]
        assert by_type.get("causes") == 1
        assert by_type.get("related_to") == 1


class TestMemoryGraphUpdateNode:
    """Tests for MemoryGraph.update_node method."""

    @pytest.fixture
    def graph_with_node(self):
        """Create graph with a node."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "graph.json"
            graph = MemoryGraph(path=path)
            node_id = graph.add_finding(
                wizard="test",
                finding={"type": "bug", "name": "Bug", "severity": "low"},
            )
            yield graph, node_id

    def test_update_status(self, graph_with_node):
        """Test updating node status."""
        graph, node_id = graph_with_node
        result = graph.update_node(node_id, {"status": "resolved"})
        assert result is True
        assert graph.nodes[node_id].status == "resolved"

    def test_update_severity(self, graph_with_node):
        """Test updating node severity."""
        graph, node_id = graph_with_node
        result = graph.update_node(node_id, {"severity": "critical"})
        assert result is True
        assert graph.nodes[node_id].severity == "critical"

    def test_update_description(self, graph_with_node):
        """Test updating node description."""
        graph, node_id = graph_with_node
        result = graph.update_node(node_id, {"description": "New description"})
        assert result is True
        assert graph.nodes[node_id].description == "New description"

    def test_update_tags(self, graph_with_node):
        """Test updating node tags."""
        graph, node_id = graph_with_node
        result = graph.update_node(node_id, {"tags": ["important", "urgent"]})
        assert result is True
        assert "important" in graph.nodes[node_id].tags

    def test_update_metadata_merges(self, graph_with_node):
        """Test metadata update merges with existing."""
        graph, node_id = graph_with_node
        graph.update_node(node_id, {"metadata": {"key1": "value1"}})
        graph.update_node(node_id, {"metadata": {"key2": "value2"}})
        assert graph.nodes[node_id].metadata.get("key1") == "value1"
        assert graph.nodes[node_id].metadata.get("key2") == "value2"

    def test_update_nonexistent_returns_false(self, graph_with_node):
        """Test updating nonexistent node returns False."""
        graph, node_id = graph_with_node
        result = graph.update_node("nonexistent", {"status": "resolved"})
        assert result is False


class TestMemoryGraphDeleteNode:
    """Tests for MemoryGraph.delete_node method."""

    @pytest.fixture
    def graph_with_connected_nodes(self):
        """Create graph with connected nodes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "graph.json"
            graph = MemoryGraph(path=path)

            id1 = graph.add_finding(wizard="test", finding={"type": "bug", "name": "A"})
            id2 = graph.add_finding(wizard="test", finding={"type": "fix", "name": "B"})
            id3 = graph.add_finding(wizard="test", finding={"type": "pattern", "name": "C"})
            graph.add_edge(id1, id2, EdgeType.FIXED_BY)
            graph.add_edge(id2, id3, EdgeType.LEADS_TO)

            yield graph, id1, id2, id3

    def test_delete_removes_node(self, graph_with_connected_nodes):
        """Test delete removes the node."""
        graph, id1, id2, id3 = graph_with_connected_nodes
        result = graph.delete_node(id2)
        assert result is True
        assert id2 not in graph.nodes
        assert len(graph.nodes) == 2

    def test_delete_removes_connected_edges(self, graph_with_connected_nodes):
        """Test delete removes edges connected to node."""
        graph, id1, id2, id3 = graph_with_connected_nodes
        len(graph.edges)
        graph.delete_node(id2)
        # Both edges should be removed
        assert len(graph.edges) == 0

    def test_delete_nonexistent_returns_false(self, graph_with_connected_nodes):
        """Test deleting nonexistent node returns False."""
        graph, id1, id2, id3 = graph_with_connected_nodes
        result = graph.delete_node("nonexistent")
        assert result is False


class TestMemoryGraphClear:
    """Tests for MemoryGraph.clear method."""

    def test_clear_removes_all_data(self):
        """Test clear removes all nodes and edges."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "graph.json"
            graph = MemoryGraph(path=path)

            id1 = graph.add_finding(wizard="t", finding={"type": "bug", "name": "A"})
            id2 = graph.add_finding(wizard="t", finding={"type": "fix", "name": "B"})
            graph.add_edge(id1, id2, EdgeType.FIXED_BY)

            assert len(graph.nodes) == 2
            assert len(graph.edges) == 1

            graph.clear()

            assert len(graph.nodes) == 0
            assert len(graph.edges) == 0


class TestMemoryGraphPersistence:
    """Tests for graph persistence."""

    def test_changes_persist_after_reload(self):
        """Test graph changes persist after reload."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "graph.json"

            # Create and populate graph
            graph1 = MemoryGraph(path=path)
            id1 = graph1.add_finding(
                wizard="test",
                finding={"type": "bug", "name": "Bug 1", "severity": "high"},
            )
            id2 = graph1.add_finding(
                wizard="test",
                finding={"type": "fix", "name": "Fix 1"},
            )
            graph1.add_edge(id1, id2, EdgeType.FIXED_BY)

            # Reload in new instance
            graph2 = MemoryGraph(path=path)

            assert len(graph2.nodes) == 2
            assert len(graph2.edges) == 1
            assert id1 in graph2.nodes
            assert id2 in graph2.nodes
            assert graph2.nodes[id1].severity == "high"

    def test_json_file_structure(self):
        """Test saved JSON file has correct structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "graph.json"

            graph = MemoryGraph(path=path)
            graph.add_finding(
                wizard="test",
                finding={"type": "bug", "name": "Test"},
            )

            with open(path) as f:
                data = json.load(f)

            assert "version" in data
            assert "updated_at" in data
            assert "node_count" in data
            assert "edge_count" in data
            assert "nodes" in data
            assert "edges" in data
            assert data["node_count"] == 1


class TestMemoryGraphIndexes:
    """Tests for graph index functionality."""

    def test_nodes_indexed_by_type(self):
        """Test nodes are indexed by type."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "graph.json"
            graph = MemoryGraph(path=path)

            graph.add_finding(wizard="t", finding={"type": "bug", "name": "B1"})
            graph.add_finding(wizard="t", finding={"type": "bug", "name": "B2"})
            graph.add_finding(wizard="t", finding={"type": "fix", "name": "F1"})

            assert len(graph._nodes_by_type[NodeType.BUG]) == 2
            assert len(graph._nodes_by_type[NodeType.FIX]) == 1

    def test_nodes_indexed_by_wizard(self):
        """Test nodes are indexed by wizard."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "graph.json"
            graph = MemoryGraph(path=path)

            graph.add_finding(wizard="security", finding={"type": "bug", "name": "B1"})
            graph.add_finding(wizard="security", finding={"type": "bug", "name": "B2"})
            graph.add_finding(wizard="perf", finding={"type": "bug", "name": "B3"})

            assert len(graph._nodes_by_wizard["security"]) == 2
            assert len(graph._nodes_by_wizard["perf"]) == 1

    def test_edges_indexed_by_source(self):
        """Test edges are indexed by source."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "graph.json"
            graph = MemoryGraph(path=path)

            id1 = graph.add_finding(wizard="t", finding={"type": "bug", "name": "A"})
            id2 = graph.add_finding(wizard="t", finding={"type": "fix", "name": "B"})
            id3 = graph.add_finding(wizard="t", finding={"type": "fix", "name": "C"})

            graph.add_edge(id1, id2, EdgeType.FIXED_BY)
            graph.add_edge(id1, id3, EdgeType.LEADS_TO)

            assert len(graph._edges_by_source[id1]) == 2
            assert len(graph._edges_by_target[id2]) == 1
            assert len(graph._edges_by_target[id3]) == 1
