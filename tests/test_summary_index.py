"""
Tests for ConversationSummaryIndex

Tests the Redis-backed conversation summary with topic indexing.
"""

import sys

import pytest

from empathy_os.memory import (
    AccessTier,
    AgentContext,
    AgentCredentials,
    ConversationSummaryIndex,
    RedisShortTermMemory,
)


@pytest.fixture
def mock_redis():
    """Create mock Redis memory for testing."""
    return RedisShortTermMemory(use_mock=True)


@pytest.fixture
def summary_index(mock_redis):
    """Create summary index with mock Redis."""
    return ConversationSummaryIndex(mock_redis)


@pytest.fixture
def credentials():
    """Create test credentials."""
    return AgentCredentials(
        agent_id="test_agent",
        tier=AccessTier.CONTRIBUTOR,
    )


class TestAgentContext:
    """Tests for AgentContext dataclass."""

    def test_to_prompt_basic(self):
        """Test basic prompt generation."""
        context = AgentContext(
            working_on="Implementing authentication",
            decisions=["Use JWT", "Redis for sessions"],
            session_id="test123",
        )

        prompt = context.to_prompt()

        assert "Session Context" in prompt
        assert "Implementing authentication" in prompt
        assert "Use JWT" in prompt
        assert "Redis for sessions" in prompt

    def test_to_prompt_with_timeline(self):
        """Test prompt with timeline events."""
        context = AgentContext(
            working_on="Testing",
            recent_events=[
                {"type": "decision", "content": "Use pytest"},
                {"type": "completed", "content": "Auth module"},
            ],
            session_id="test123",
        )

        prompt = context.to_prompt()

        assert "Recent timeline" in prompt
        assert "Decision: Use pytest" in prompt
        assert "Completed: Auth module" in prompt

    def test_to_prompt_with_files(self):
        """Test prompt with key files."""
        context = AgentContext(
            working_on="Refactoring",
            relevant_files=["auth.py", "models.py", "tests/test_auth.py"],
            session_id="test123",
        )

        prompt = context.to_prompt()

        assert "Key files:" in prompt
        assert "auth.py" in prompt
        assert "models.py" in prompt

    def test_to_dict(self):
        """Test dictionary conversion."""
        context = AgentContext(
            working_on="Testing",
            decisions=["Use pytest"],
            topics=["testing"],
            session_id="test123",
        )

        d = context.to_dict()

        assert d["working_on"] == "Testing"
        assert d["decisions"] == ["Use pytest"]
        assert d["topics"] == ["testing"]
        assert d["session_id"] == "test123"


class TestConversationSummaryIndex:
    """Tests for ConversationSummaryIndex."""

    def test_update_summary_decision(self, summary_index):
        """Test updating summary with a decision."""
        result = summary_index.update_summary(
            "session123",
            {
                "type": "decision",
                "content": "Use JWT for authentication",
            },
        )

        assert result is True

        # Verify context has the decision
        context = summary_index.get_context_for_agent("session123")
        assert "Use JWT for authentication" in context.decisions

    def test_update_summary_started(self, summary_index):
        """Test updating summary with started event."""
        summary_index.update_summary(
            "session123",
            {
                "type": "started",
                "content": "Implementing user authentication",
            },
        )

        context = summary_index.get_context_for_agent("session123")
        assert context.working_on == "Implementing user authentication"

    def test_update_summary_question(self, summary_index):
        """Test updating summary with question."""
        summary_index.update_summary(
            "session123",
            {
                "type": "question",
                "content": "Should we use Redis for sessions?",
            },
        )

        context = summary_index.get_context_for_agent("session123")
        assert "Should we use Redis for sessions?" in context.open_questions

    def test_update_summary_file_modified(self, summary_index):
        """Test updating summary with file modification."""
        summary_index.update_summary(
            "session123",
            {
                "type": "file_modified",
                "content": "auth.py",
            },
        )

        context = summary_index.get_context_for_agent("session123")
        assert "auth.py" in context.relevant_files

    @pytest.mark.skipif(sys.platform == "win32", reason="Timeline ordering differs on Windows")
    def test_timeline_ordering(self, summary_index):
        """Test that timeline events are ordered correctly."""
        # Add events in sequence
        summary_index.update_summary(
            "session123",
            {
                "type": "started",
                "content": "First event",
            },
        )
        summary_index.update_summary(
            "session123",
            {
                "type": "decision",
                "content": "Second event",
            },
        )
        summary_index.update_summary(
            "session123",
            {
                "type": "completed",
                "content": "Third event",
            },
        )

        context = summary_index.get_context_for_agent("session123")

        # Most recent should be first
        assert len(context.recent_events) == 3
        assert context.recent_events[0]["content"] == "Third event"

    def test_topic_extraction(self, summary_index):
        """Test automatic topic extraction."""
        summary_index.update_summary(
            "session123",
            {
                "type": "decision",
                "content": "Use JWT authentication with Redis sessions",
            },
        )

        context = summary_index.get_context_for_agent("session123")

        assert "auth" in context.topics
        assert "database" in context.topics  # Redis is a database keyword

    def test_topic_indexing(self, summary_index):
        """Test topic-based session indexing."""
        # Create sessions with different topics
        summary_index.update_summary(
            "session1",
            {
                "type": "decision",
                "content": "Use JWT authentication",
            },
        )
        summary_index.update_summary(
            "session2",
            {
                "type": "decision",
                "content": "Optimize database queries",
            },
        )
        summary_index.update_summary(
            "session3",
            {
                "type": "decision",
                "content": "Fix authentication bug",
            },
        )

        # Find sessions by topic
        auth_sessions = summary_index.get_sessions_by_topic("auth")

        assert "session1" in auth_sessions
        assert "session3" in auth_sessions
        assert "session2" not in auth_sessions

    def test_context_topic_filtering(self, summary_index):
        """Test filtering context by focus topics."""
        # Add various decisions
        summary_index.update_summary(
            "session123",
            {
                "type": "decision",
                "content": "Use JWT for authentication",
            },
        )
        summary_index.update_summary(
            "session123",
            {
                "type": "decision",
                "content": "Optimize database queries",
            },
        )
        summary_index.update_summary(
            "session123",
            {
                "type": "decision",
                "content": "Add login rate limiting",
            },
        )

        # Get context filtered to auth
        context = summary_index.get_context_for_agent(
            "session123",
            focus_topics=["auth", "login"],
        )

        # Should include auth-related decisions
        assert any("JWT" in d for d in context.decisions)
        assert any("login" in d.lower() for d in context.decisions)

    def test_recall_decisions(self, summary_index):
        """Test cross-session decision recall."""
        # Create sessions with decisions
        summary_index.update_summary(
            "session1",
            {
                "type": "decision",
                "content": "Use JWT for authentication",
            },
        )
        summary_index.update_summary(
            "session2",
            {
                "type": "decision",
                "content": "Use OAuth for external auth",
            },
        )

        # Recall auth-related decisions
        decisions = summary_index.recall_decisions("auth")

        assert len(decisions) >= 2
        assert any("JWT" in d["decision"] for d in decisions)
        assert any("OAuth" in d["decision"] for d in decisions)

    def test_clear_session(self, summary_index):
        """Test clearing session data."""
        # Create session with data
        summary_index.update_summary(
            "session123",
            {
                "type": "decision",
                "content": "Use JWT authentication",
            },
        )

        # Verify data exists
        context = summary_index.get_context_for_agent("session123")
        assert len(context.decisions) > 0

        # Clear session
        result = summary_index.clear_session("session123")
        assert result is True

        # Verify data is gone
        context = summary_index.get_context_for_agent("session123")
        assert len(context.decisions) == 0

    def test_multiple_decisions_limit(self, summary_index):
        """Test that decisions are limited to prevent overflow."""
        # Add many decisions
        for i in range(30):
            summary_index.update_summary(
                "session123",
                {
                    "type": "decision",
                    "content": f"Decision {i}",
                },
            )

        context = summary_index.get_context_for_agent("session123")

        # Should be capped at 20
        assert len(context.decisions) <= 20
        # Should have most recent
        assert "Decision 29" in context.decisions

    def test_empty_session(self, summary_index):
        """Test getting context for non-existent session."""
        context = summary_index.get_context_for_agent("nonexistent")

        assert context.working_on == ""
        assert context.decisions == []
        assert context.recent_events == []


class TestIntegration:
    """Integration tests for summary index."""

    def test_full_workflow(self, summary_index):
        """Test a complete session workflow."""
        session_id = "workflow_test"

        # Start task
        summary_index.update_summary(
            session_id,
            {
                "type": "started",
                "content": "Implementing user authentication system",
            },
        )

        # Make decisions
        summary_index.update_summary(
            session_id,
            {
                "type": "decision",
                "content": "Use JWT tokens for auth",
            },
        )
        summary_index.update_summary(
            session_id,
            {
                "type": "decision",
                "content": "Store sessions in Redis",
            },
        )

        # Ask questions
        summary_index.update_summary(
            session_id,
            {
                "type": "question",
                "content": "How to handle token refresh?",
            },
        )

        # Modify files
        summary_index.update_summary(
            session_id,
            {
                "type": "file_modified",
                "content": "auth/jwt.py",
            },
        )
        summary_index.update_summary(
            session_id,
            {
                "type": "file_modified",
                "content": "auth/middleware.py",
            },
        )

        # Complete work
        summary_index.update_summary(
            session_id,
            {
                "type": "completed",
                "content": "JWT token generation",
            },
        )

        # Get context
        context = summary_index.get_context_for_agent(session_id)

        assert context.working_on == "Implementing user authentication system"
        assert len(context.decisions) == 2
        assert len(context.open_questions) == 1
        assert len(context.relevant_files) == 2
        assert len(context.recent_events) >= 5

        # Verify prompt is well-formed
        prompt = context.to_prompt()
        assert "JWT" in prompt
        assert "Redis" in prompt
        assert "token refresh" in prompt

    def test_cross_session_knowledge(self, summary_index):
        """Test that knowledge persists across sessions."""
        # Session 1: Make auth decisions (includes 'auth' keyword for topic extraction)
        summary_index.update_summary(
            "session1",
            {
                "type": "decision",
                "content": "Use JWT authentication with 15-minute expiry",
            },
        )

        # Session 2: Different topic
        summary_index.update_summary(
            "session2",
            {
                "type": "decision",
                "content": "Optimize database connection pooling",
            },
        )

        # Session 3: Related to session 1
        summary_index.update_summary(
            "session3",
            {
                "type": "question",
                "content": "What was the auth token expiry decision?",
            },
        )

        # Should find auth decisions (topic 'auth' is indexed)
        auth_decisions = summary_index.recall_decisions("auth")

        assert len(auth_decisions) >= 1
        assert any("15-minute" in d["decision"] for d in auth_decisions)
