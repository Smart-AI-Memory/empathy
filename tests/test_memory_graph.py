"""Tests for Memory Graph - Cross-Wizard Intelligence

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import tempfile
from pathlib import Path

import pytest

from empathy_os.memory import Edge, EdgeType, MemoryGraph, Node, NodeType


@pytest.fixture
def temp_graph_path():
    """Create a temporary path for test graph."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        return Path(f.name)


@pytest.fixture
def graph(temp_graph_path):
    """Create a fresh graph for testing."""
    return MemoryGraph(path=temp_graph_path)


class TestMemoryGraph:
    """Tests for MemoryGraph class."""

    def test_init_creates_empty_graph(self, graph):
        """Test that initialization creates an empty graph."""
        assert len(graph.nodes) == 0
        assert len(graph.edges) == 0

    def test_add_finding_creates_node(self, graph):
        """Test adding a finding creates a node."""
        node_id = graph.add_finding(
            wizard="security-audit",
            finding={
                "type": "vulnerability",
                "name": "SQL Injection",
                "description": "User input not sanitized",
                "file": "src/db/query.py",
                "line": 42,
                "severity": "critical",
            },
        )

        assert node_id is not None
        assert node_id in graph.nodes

        node = graph.get_node(node_id)
        assert node.name == "SQL Injection"
        assert node.type == NodeType.VULNERABILITY
        assert node.severity == "critical"
        assert node.source_wizard == "security-audit"

    def test_add_edge_connects_nodes(self, graph):
        """Test adding an edge connects two nodes."""
        bug_id = graph.add_finding(
            wizard="bug-predict",
            finding={"type": "bug", "name": "Null reference"},
        )

        fix_id = graph.add_finding(
            wizard="bug-predict",
            finding={"type": "fix", "name": "Add null check"},
        )

        edge_id = graph.add_edge(bug_id, fix_id, EdgeType.FIXED_BY)

        assert edge_id is not None
        assert len(graph.edges) == 1

    def test_add_edge_bidirectional(self, graph):
        """Test bidirectional edge creation."""
        node1 = graph.add_finding(
            wizard="test",
            finding={"type": "bug", "name": "Bug A"},
        )

        node2 = graph.add_finding(
            wizard="test",
            finding={"type": "bug", "name": "Bug B"},
        )

        graph.add_edge(node1, node2, EdgeType.SIMILAR_TO, bidirectional=True)

        # Should have 2 edges
        assert len(graph.edges) == 2

    def test_find_related_outgoing(self, graph):
        """Test finding related nodes via outgoing edges."""
        parent = graph.add_finding(
            wizard="test",
            finding={"type": "file", "name": "auth.py"},
        )

        child1 = graph.add_finding(
            wizard="test",
            finding={"type": "function", "name": "login()"},
        )

        child2 = graph.add_finding(
            wizard="test",
            finding={"type": "function", "name": "logout()"},
        )

        graph.add_edge(parent, child1, EdgeType.CONTAINS)
        graph.add_edge(parent, child2, EdgeType.CONTAINS)

        related = graph.find_related(parent, direction="outgoing")

        assert len(related) == 2
        assert any(n.name == "login()" for n in related)
        assert any(n.name == "logout()" for n in related)

    def test_find_related_with_edge_filter(self, graph):
        """Test filtering related nodes by edge type."""
        bug = graph.add_finding(
            wizard="test",
            finding={"type": "bug", "name": "Bug"},
        )

        fix = graph.add_finding(
            wizard="test",
            finding={"type": "fix", "name": "Fix"},
        )

        similar = graph.add_finding(
            wizard="test",
            finding={"type": "bug", "name": "Similar Bug"},
        )

        graph.add_edge(bug, fix, EdgeType.FIXED_BY)
        graph.add_edge(bug, similar, EdgeType.SIMILAR_TO)

        # Only find fixes
        fixes = graph.find_related(bug, edge_types=[EdgeType.FIXED_BY])
        assert len(fixes) == 1
        assert fixes[0].name == "Fix"

    def test_find_similar(self, graph):
        """Test finding similar nodes."""
        graph.add_finding(
            wizard="test",
            finding={
                "type": "bug",
                "name": "Null reference in auth module",
                "description": "Missing null check",
            },
        )

        graph.add_finding(
            wizard="test",
            finding={
                "type": "bug",
                "name": "Type error in utils",
                "description": "Wrong type passed",
            },
        )

        # Search for similar
        results = graph.find_similar(
            {"name": "Null reference error", "description": "null check missing"},
            threshold=0.3,
        )

        assert len(results) >= 1
        # First result should be the null reference bug
        assert "null" in results[0][0].name.lower()

    def test_find_by_type(self, graph):
        """Test finding nodes by type."""
        graph.add_finding(wizard="test", finding={"type": "bug", "name": "Bug 1"})
        graph.add_finding(wizard="test", finding={"type": "bug", "name": "Bug 2"})
        graph.add_finding(wizard="test", finding={"type": "fix", "name": "Fix 1"})

        bugs = graph.find_by_type(NodeType.BUG)
        assert len(bugs) == 2

    def test_find_by_wizard(self, graph):
        """Test finding nodes by source wizard."""
        graph.add_finding(wizard="security-audit", finding={"type": "vulnerability", "name": "V1"})
        graph.add_finding(wizard="security-audit", finding={"type": "vulnerability", "name": "V2"})
        graph.add_finding(wizard="bug-predict", finding={"type": "bug", "name": "B1"})

        security_nodes = graph.find_by_wizard("security-audit")
        assert len(security_nodes) == 2

    def test_get_path(self, graph):
        """Test finding path between nodes."""
        a = graph.add_finding(wizard="test", finding={"type": "bug", "name": "A"})
        b = graph.add_finding(wizard="test", finding={"type": "bug", "name": "B"})
        c = graph.add_finding(wizard="test", finding={"type": "fix", "name": "C"})

        graph.add_edge(a, b, EdgeType.CAUSES)
        graph.add_edge(b, c, EdgeType.FIXED_BY)

        path = graph.get_path(a, c)

        assert len(path) == 3
        assert path[0][0].name == "A"
        assert path[2][0].name == "C"

    def test_update_node(self, graph):
        """Test updating node properties."""
        node_id = graph.add_finding(
            wizard="test",
            finding={"type": "bug", "name": "Bug", "severity": "medium"},
        )

        graph.update_node(node_id, {"status": "resolved", "severity": "low"})

        node = graph.get_node(node_id)
        assert node.status == "resolved"
        assert node.severity == "low"

    def test_delete_node(self, graph):
        """Test deleting a node and its edges."""
        a = graph.add_finding(wizard="test", finding={"type": "bug", "name": "A"})
        b = graph.add_finding(wizard="test", finding={"type": "fix", "name": "B"})

        graph.add_edge(a, b, EdgeType.FIXED_BY)

        assert len(graph.nodes) == 2
        assert len(graph.edges) == 1

        graph.delete_node(a)

        assert len(graph.nodes) == 1
        assert len(graph.edges) == 0
        assert a not in graph.nodes

    def test_get_statistics(self, graph):
        """Test getting graph statistics."""
        graph.add_finding(
            wizard="security",
            finding={"type": "vulnerability", "name": "V1", "severity": "high"},
        )
        graph.add_finding(
            wizard="security",
            finding={"type": "vulnerability", "name": "V2", "severity": "critical"},
        )
        graph.add_finding(wizard="bugs", finding={"type": "bug", "name": "B1", "severity": "high"})

        stats = graph.get_statistics()

        assert stats["total_nodes"] == 3
        assert stats["nodes_by_type"]["vulnerability"] == 2
        assert stats["nodes_by_type"]["bug"] == 1
        assert stats["nodes_by_wizard"]["security"] == 2
        assert stats["nodes_by_severity"]["high"] == 2

    def test_persistence(self, temp_graph_path):
        """Test that graph persists across instances."""
        # Create graph and add data
        graph1 = MemoryGraph(path=temp_graph_path)
        node_id = graph1.add_finding(
            wizard="test",
            finding={"type": "bug", "name": "Persistent Bug"},
        )

        # Create new instance
        graph2 = MemoryGraph(path=temp_graph_path)

        assert node_id in graph2.nodes
        assert graph2.get_node(node_id).name == "Persistent Bug"

    def test_clear(self, graph):
        """Test clearing the graph."""
        graph.add_finding(wizard="test", finding={"type": "bug", "name": "Bug"})
        graph.add_finding(wizard="test", finding={"type": "fix", "name": "Fix"})

        graph.clear()

        assert len(graph.nodes) == 0
        assert len(graph.edges) == 0


class TestNodeTypes:
    """Tests for Node type definitions."""

    def test_node_to_dict(self):
        """Test node serialization."""
        node = Node(
            id="test_123",
            type=NodeType.BUG,
            name="Test Bug",
            description="A test bug",
            source_wizard="test",
            severity="high",
        )

        data = node.to_dict()

        assert data["id"] == "test_123"
        assert data["type"] == "bug"
        assert data["name"] == "Test Bug"
        assert data["severity"] == "high"

    def test_node_from_dict(self):
        """Test node deserialization."""
        data = {
            "id": "test_123",
            "type": "vulnerability",
            "name": "Test Vuln",
            "description": "A vulnerability",
            "source_wizard": "security",
            "severity": "critical",
            "created_at": "2025-01-01T00:00:00",
            "updated_at": "2025-01-01T00:00:00",
        }

        node = Node.from_dict(data)

        assert node.id == "test_123"
        assert node.type == NodeType.VULNERABILITY
        assert node.name == "Test Vuln"


class TestEdgeTypes:
    """Tests for Edge type definitions."""

    def test_edge_to_dict(self):
        """Test edge serialization."""
        edge = Edge(
            source_id="node_1",
            target_id="node_2",
            type=EdgeType.FIXED_BY,
            weight=0.9,
            description="Fix resolves bug",
        )

        data = edge.to_dict()

        assert data["source_id"] == "node_1"
        assert data["target_id"] == "node_2"
        assert data["type"] == "fixed_by"
        assert data["weight"] == 0.9

    def test_edge_from_dict(self):
        """Test edge deserialization."""
        data = {
            "source_id": "a",
            "target_id": "b",
            "type": "causes",
            "weight": 0.8,
            "created_at": "2025-01-01T00:00:00",
        }

        edge = Edge.from_dict(data)

        assert edge.source_id == "a"
        assert edge.target_id == "b"
        assert edge.type == EdgeType.CAUSES
