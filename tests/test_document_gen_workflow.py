"""
Tests for DocumentGenerationWorkflow.

Tests the multi-tier documentation generation pipeline with:
- Outline generation
- Content writing (chunked and non-chunked)
- Polish stage with cost tracking
- Export functionality

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.empathy_os.workflows.base import ModelTier
from src.empathy_os.workflows.document_gen import (
    TOKEN_COSTS,
    DocumentGenerationWorkflow,
    format_doc_gen_report,
)


class TestTokenCosts:
    """Tests for token cost constants."""

    def test_token_costs_exist(self):
        """Test that token costs are defined for all tiers."""
        assert ModelTier.CHEAP in TOKEN_COSTS
        assert ModelTier.CAPABLE in TOKEN_COSTS
        assert ModelTier.PREMIUM in TOKEN_COSTS

    def test_token_costs_structure(self):
        """Test that token costs have input and output keys."""
        for tier in [ModelTier.CHEAP, ModelTier.CAPABLE, ModelTier.PREMIUM]:
            assert "input" in TOKEN_COSTS[tier]
            assert "output" in TOKEN_COSTS[tier]
            assert TOKEN_COSTS[tier]["input"] > 0 or tier == ModelTier.CHEAP
            assert TOKEN_COSTS[tier]["output"] > 0

    def test_tier_cost_ordering(self):
        """Test that premium costs more than capable costs more than cheap."""
        assert TOKEN_COSTS[ModelTier.PREMIUM]["input"] > TOKEN_COSTS[ModelTier.CAPABLE]["input"]
        assert TOKEN_COSTS[ModelTier.CAPABLE]["input"] > TOKEN_COSTS[ModelTier.CHEAP]["input"]


class TestDocumentGenerationWorkflowInit:
    """Tests for DocumentGenerationWorkflow initialization."""

    def test_default_init(self):
        """Test default initialization."""
        workflow = DocumentGenerationWorkflow()

        assert workflow.name == "doc-gen"
        assert workflow.skip_polish_threshold == 1000
        assert workflow.max_sections == 10
        assert workflow.chunked_generation is True
        assert workflow.sections_per_chunk == 3
        assert workflow.max_cost == 5.0
        assert workflow.graceful_degradation is True

    def test_custom_skip_polish_threshold(self):
        """Test custom skip polish threshold."""
        workflow = DocumentGenerationWorkflow(skip_polish_threshold=500)

        assert workflow.skip_polish_threshold == 500

    def test_custom_max_sections(self):
        """Test custom max sections."""
        workflow = DocumentGenerationWorkflow(max_sections=20)

        assert workflow.max_sections == 20

    def test_custom_max_write_tokens(self):
        """Test custom max write tokens."""
        workflow = DocumentGenerationWorkflow(max_write_tokens=32000)

        assert workflow.max_write_tokens == 32000
        assert workflow._user_max_write_tokens == 32000

    def test_section_focus(self):
        """Test section focus configuration."""
        focus = ["API Reference", "Testing Guide"]
        workflow = DocumentGenerationWorkflow(section_focus=focus)

        assert workflow.section_focus == focus

    def test_export_path(self):
        """Test export path configuration."""
        workflow = DocumentGenerationWorkflow(export_path="/docs/generated")

        assert workflow.export_path == Path("/docs/generated")

    def test_export_path_none(self):
        """Test export path defaults to None."""
        workflow = DocumentGenerationWorkflow()

        assert workflow.export_path is None

    def test_tier_map(self):
        """Test tier mapping for stages."""
        workflow = DocumentGenerationWorkflow()

        assert workflow.tier_map["outline"] == ModelTier.CHEAP
        assert workflow.tier_map["write"] == ModelTier.CAPABLE
        assert workflow.tier_map["polish"] == ModelTier.PREMIUM

    def test_stages(self):
        """Test workflow stages."""
        workflow = DocumentGenerationWorkflow()

        assert workflow.stages == ["outline", "write", "polish"]


class TestDocumentGenerationCostTracking:
    """Tests for cost tracking functionality."""

    def test_estimate_cost(self):
        """Test cost estimation."""
        workflow = DocumentGenerationWorkflow()

        cost = workflow._estimate_cost(ModelTier.CAPABLE, 1000, 500)

        # Capable tier: input=0.003, output=0.015 per 1k tokens
        expected = (1000 / 1000) * 0.003 + (500 / 1000) * 0.015
        assert cost == pytest.approx(expected)

    def test_track_cost_accumulates(self):
        """Test that cost tracking accumulates."""
        workflow = DocumentGenerationWorkflow()

        workflow._track_cost(ModelTier.CHEAP, 1000, 500)
        cost1 = workflow._accumulated_cost

        workflow._track_cost(ModelTier.CHEAP, 1000, 500)
        cost2 = workflow._accumulated_cost

        assert cost2 > cost1
        assert cost2 == pytest.approx(cost1 * 2)

    def test_track_cost_warning_threshold(self):
        """Test cost warning at threshold."""
        workflow = DocumentGenerationWorkflow(max_cost=1.0, cost_warning_threshold=0.5)

        # Should not warn yet
        workflow._track_cost(ModelTier.CAPABLE, 100, 50)
        assert workflow._cost_warning_issued is False

        # Force accumulated cost over threshold
        workflow._accumulated_cost = 0.6
        workflow._track_cost(ModelTier.CAPABLE, 100, 50)
        assert workflow._cost_warning_issued is True

    def test_track_cost_returns_should_stop(self):
        """Test cost tracking returns should_stop when limit reached."""
        workflow = DocumentGenerationWorkflow(max_cost=0.01)

        # Small cost should not stop
        _, should_stop = workflow._track_cost(ModelTier.CHEAP, 100, 50)
        assert should_stop is False

        # Large cost should trigger stop
        workflow._accumulated_cost = 0.02
        _, should_stop = workflow._track_cost(ModelTier.PREMIUM, 10000, 10000)
        assert should_stop is True

    def test_track_cost_no_limit(self):
        """Test cost tracking with no limit (max_cost=0)."""
        workflow = DocumentGenerationWorkflow(max_cost=0)

        workflow._accumulated_cost = 100.0  # Very high cost
        _, should_stop = workflow._track_cost(ModelTier.PREMIUM, 10000, 10000)

        assert should_stop is False  # Never stops


class TestDocumentGenerationAutoScale:
    """Tests for auto-scaling functionality."""

    def test_auto_scale_minimum(self):
        """Test auto-scaling enforces minimum."""
        workflow = DocumentGenerationWorkflow()

        scaled = workflow._auto_scale_tokens(3)

        assert scaled >= 16000

    def test_auto_scale_maximum(self):
        """Test auto-scaling enforces maximum."""
        workflow = DocumentGenerationWorkflow()

        scaled = workflow._auto_scale_tokens(100)

        assert scaled <= 64000

    def test_auto_scale_proportional(self):
        """Test auto-scaling is proportional to sections."""
        workflow = DocumentGenerationWorkflow()

        scaled_small = workflow._auto_scale_tokens(5)
        scaled_large = workflow._auto_scale_tokens(20)

        assert scaled_large > scaled_small

    def test_auto_scale_respects_user_override(self):
        """Test auto-scaling respects user-specified max_write_tokens."""
        workflow = DocumentGenerationWorkflow(max_write_tokens=8000)

        scaled = workflow._auto_scale_tokens(50)

        assert scaled == 8000


class TestDocumentGenerationStages:
    """Tests for workflow stage routing."""

    @pytest.mark.asyncio
    async def test_run_stage_outline(self):
        """Test outline stage routing."""
        workflow = DocumentGenerationWorkflow()

        with patch.object(workflow, "_outline", new_callable=AsyncMock) as mock:
            mock.return_value = ({"outline": "test"}, 100, 50)

            await workflow.run_stage("outline", ModelTier.CHEAP, {"source_code": "..."})

            mock.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_stage_write(self):
        """Test write stage routing."""
        workflow = DocumentGenerationWorkflow()

        with patch.object(workflow, "_write", new_callable=AsyncMock) as mock:
            mock.return_value = ({"draft_document": "..."}, 200, 100)

            await workflow.run_stage("write", ModelTier.CAPABLE, {"outline": "..."})

            mock.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_stage_polish(self):
        """Test polish stage routing."""
        workflow = DocumentGenerationWorkflow()

        with patch.object(workflow, "_polish", new_callable=AsyncMock) as mock:
            mock.return_value = ({"document": "..."}, 300, 150)

            await workflow.run_stage("polish", ModelTier.PREMIUM, {"draft_document": "..."})

            mock.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_stage_invalid(self):
        """Test invalid stage raises error."""
        workflow = DocumentGenerationWorkflow()

        with pytest.raises(ValueError, match="Unknown stage"):
            await workflow.run_stage("invalid", ModelTier.CHEAP, {})


class TestDocumentGenerationOutline:
    """Tests for outline generation stage."""

    @pytest.mark.asyncio
    async def test_outline_from_source_code(self):
        """Test outline generation from source code."""
        workflow = DocumentGenerationWorkflow()

        with patch.object(workflow, "_call_llm", new_callable=AsyncMock) as mock:
            mock.return_value = ("1. Introduction\n2. API Reference", 100, 50)

            result, input_tokens, output_tokens = await workflow._outline(
                {
                    "source_code": "def hello(): pass",
                    "doc_type": "api_reference",
                    "audience": "developers",
                },
                ModelTier.CHEAP,
            )

            assert "outline" in result
            assert result["doc_type"] == "api_reference"
            assert result["audience"] == "developers"
            mock.assert_called_once()

    @pytest.mark.asyncio
    async def test_outline_reads_file_target(self):
        """Test outline reads file when target is a file path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("def example(): pass")

            workflow = DocumentGenerationWorkflow()

            with patch.object(workflow, "_call_llm", new_callable=AsyncMock) as mock:
                mock.return_value = ("1. Introduction", 100, 50)

                result, _, _ = await workflow._outline(
                    {
                        "target": str(test_file),
                        "doc_type": "api_reference",
                        "audience": "developers",
                    },
                    ModelTier.CHEAP,
                )

                # The file content should be read
                assert "def example" in result["content_to_document"]


class TestDocumentGenerationParseSections:
    """Tests for section parsing from outlines."""

    def test_parse_outline_sections_basic(self):
        """Test parsing basic numbered outline."""
        workflow = DocumentGenerationWorkflow()

        outline = """1. Introduction
2. Getting Started
3. API Reference
4. Testing Guide"""

        sections = workflow._parse_outline_sections(outline)

        assert len(sections) == 4
        assert sections[0] == "Introduction"
        assert sections[1] == "Getting Started"

    def test_parse_outline_sections_with_descriptions(self):
        """Test parsing outline with descriptions after dash."""
        workflow = DocumentGenerationWorkflow()

        outline = """1. Introduction - Overview of the project
2. Installation - How to install the package
3. Usage - Basic usage examples"""

        sections = workflow._parse_outline_sections(outline)

        assert len(sections) == 3
        assert sections[0] == "Introduction"
        assert sections[1] == "Installation"
        assert sections[2] == "Usage"

    def test_parse_outline_sections_ignores_subsections(self):
        """Test that subsections (1.1, 2.1, etc.) are ignored."""
        workflow = DocumentGenerationWorkflow()

        outline = """1. Introduction
1.1 Background
1.2 Purpose
2. Getting Started
2.1 Prerequisites
2.2 Installation"""

        sections = workflow._parse_outline_sections(outline)

        # Should only get top-level sections
        assert len(sections) == 2
        assert "Introduction" in sections
        assert "Getting Started" in sections

    def test_parse_outline_sections_empty(self):
        """Test parsing empty outline."""
        workflow = DocumentGenerationWorkflow()

        sections = workflow._parse_outline_sections("")

        assert sections == []


class TestDocumentGenerationWrite:
    """Tests for write stage."""

    @pytest.mark.asyncio
    async def test_write_basic(self):
        """Test basic write stage."""
        workflow = DocumentGenerationWorkflow()

        with patch.object(workflow, "_call_llm", new_callable=AsyncMock) as mock:
            mock.return_value = ("# Introduction\n\nContent here...", 200, 100)

            result, _, output_tokens = await workflow._write(
                {
                    "outline": "1. Introduction\n2. Setup",
                    "doc_type": "api_reference",
                    "audience": "developers",
                    "content_to_document": "def hello(): pass",
                },
                ModelTier.CAPABLE,
            )

            assert "draft_document" in result
            assert result["chunked"] is False
            mock.assert_called_once()

    @pytest.mark.asyncio
    async def test_write_with_section_focus(self):
        """Test write with section focus."""
        workflow = DocumentGenerationWorkflow(section_focus=["API Reference"])

        with patch.object(workflow, "_call_llm", new_callable=AsyncMock) as mock:
            mock.return_value = ("# API Reference\n\nContent...", 200, 100)

            await workflow._write(
                {"outline": "1. Intro\n2. API Reference\n3. Testing", "doc_type": "api"},
                ModelTier.CAPABLE,
            )

            # Check that section focus is mentioned in the call
            call_args = mock.call_args
            assert "API Reference" in call_args[0][1]  # Should be in system message


class TestDocumentGenerationWriteChunked:
    """Tests for chunked write functionality."""

    @pytest.mark.asyncio
    async def test_write_chunked_triggers_for_large_outlines(self):
        """Test that chunked writing triggers for large outlines."""
        workflow = DocumentGenerationWorkflow(sections_per_chunk=2)

        # Create outline with more than sections_per_chunk * 2 sections
        outline = "\n".join([f"{i}. Section {i}" for i in range(1, 8)])

        with patch.object(workflow, "_write_chunked", new_callable=AsyncMock) as mock_chunked:
            mock_chunked.return_value = ({"draft_document": "...", "chunked": True}, 500, 300)

            result, _, _ = await workflow._write(
                {"outline": outline, "doc_type": "guide"},
                ModelTier.CAPABLE,
            )

            mock_chunked.assert_called_once()
            assert result["chunked"] is True

    @pytest.mark.asyncio
    async def test_write_chunked_combines_content(self):
        """Test that chunked write combines all chunks."""
        workflow = DocumentGenerationWorkflow(sections_per_chunk=2, max_cost=100)

        sections = ["Section A", "Section B", "Section C", "Section D"]

        with patch.object(workflow, "_call_llm", new_callable=AsyncMock) as mock:
            mock.return_value = ("## Content", 100, 50)

            result, _, _ = await workflow._write_chunked(
                sections=sections,
                outline="outline",
                doc_type="guide",
                audience="developers",
                content_to_document="source",
                tier=ModelTier.CAPABLE,
            )

            # Should have made multiple calls (one per chunk)
            assert mock.call_count == 2  # 4 sections / 2 per chunk = 2 chunks
            assert "draft_document" in result
            assert result["chunked"] is True

    @pytest.mark.asyncio
    async def test_write_chunked_stops_on_cost_limit(self):
        """Test that chunked write stops when cost limit reached."""
        workflow = DocumentGenerationWorkflow(sections_per_chunk=2, max_cost=0.001)

        sections = ["Section A", "Section B", "Section C", "Section D"]

        with patch.object(workflow, "_call_llm", new_callable=AsyncMock) as mock:
            mock.return_value = ("## Content", 1000, 1000)  # High token count

            result, _, _ = await workflow._write_chunked(
                sections=sections,
                outline="outline",
                doc_type="guide",
                audience="developers",
                content_to_document="source",
                tier=ModelTier.CAPABLE,
            )

            # Should have stopped early
            assert result["stopped_early"] is True
            assert "warning" in result


class TestDocumentGenerationPolish:
    """Tests for polish stage."""

    @pytest.mark.asyncio
    async def test_polish_basic(self):
        """Test basic polish stage."""
        workflow = DocumentGenerationWorkflow()
        workflow._api_key = None  # Force LLM call path

        with patch.object(workflow, "_call_llm", new_callable=AsyncMock) as mock:
            mock.return_value = ("# Polished Document\n\nContent...", 300, 200)

            result, _, _ = await workflow._polish(
                {
                    "draft_document": "# Draft\n\nContent",
                    "doc_type": "api_reference",
                    "audience": "developers",
                },
                ModelTier.PREMIUM,
            )

            assert "document" in result
            assert result["model_tier_used"] == "premium"
            mock.assert_called_once()

    @pytest.mark.asyncio
    async def test_polish_generates_formatted_report(self):
        """Test that polish generates a formatted report."""
        workflow = DocumentGenerationWorkflow()
        workflow._api_key = None

        with patch.object(workflow, "_call_llm", new_callable=AsyncMock) as mock:
            mock.return_value = ("# Polished", 100, 50)

            result, _, _ = await workflow._polish(
                {"draft_document": "Draft", "doc_type": "guide", "audience": "users"},
                ModelTier.PREMIUM,
            )

            assert "formatted_report" in result
            assert "DOCUMENTATION GENERATION REPORT" in result["formatted_report"]


class TestDocumentGenerationExport:
    """Tests for document export functionality."""

    def test_export_document_disabled(self):
        """Test export when export_path is None."""
        workflow = DocumentGenerationWorkflow()

        doc_path, report_path = workflow._export_document("content", "api_reference")

        assert doc_path is None
        assert report_path is None

    def test_export_document_creates_files(self):
        """Test export creates documentation files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            workflow = DocumentGenerationWorkflow(export_path=tmpdir)

            doc_path, report_path = workflow._export_document(
                document="# API Reference\n\nContent here",
                doc_type="api_reference",
                report="Report content",
            )

            assert doc_path is not None
            assert doc_path.exists()
            assert "api_reference" in doc_path.name
            assert doc_path.suffix == ".md"

            assert report_path is not None
            assert report_path.exists()

    def test_export_document_creates_directory(self):
        """Test export creates export directory if missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            export_dir = Path(tmpdir) / "docs" / "generated"
            workflow = DocumentGenerationWorkflow(export_path=export_dir)

            doc_path, _ = workflow._export_document("content", "guide")

            assert export_dir.exists()
            assert doc_path is not None


class TestDocumentGenerationChunkOutput:
    """Tests for output chunking for display."""

    def test_chunk_output_small_content(self):
        """Test that small content is not chunked."""
        workflow = DocumentGenerationWorkflow(max_display_chars=1000)

        content = "Small content"
        chunks = workflow._chunk_output_for_display(content)

        assert len(chunks) == 1
        assert chunks[0] == content

    def test_chunk_output_large_content(self):
        """Test that large content is chunked."""
        workflow = DocumentGenerationWorkflow(max_display_chars=100)

        content = "## Section 1\n\n" + "A" * 60 + "\n\n## Section 2\n\n" + "B" * 60

        chunks = workflow._chunk_output_for_display(content)

        assert len(chunks) > 1
        for chunk in chunks:
            assert "PART" in chunk or len(chunk) <= workflow.max_display_chars + 100


class TestDocumentGenerationSkipStage:
    """Tests for stage skipping logic."""

    def test_should_skip_polish_short_doc(self):
        """Test that short documents change polish tier."""
        workflow = DocumentGenerationWorkflow(skip_polish_threshold=500)
        workflow._total_content_tokens = 100

        skip, reason = workflow.should_skip_stage("polish", {})

        # Polish is not skipped but tier may be changed
        assert skip is False
        assert workflow.tier_map["polish"] == ModelTier.CAPABLE  # Downgraded

    def test_should_not_skip_other_stages(self):
        """Test that other stages are never skipped."""
        workflow = DocumentGenerationWorkflow()

        skip, reason = workflow.should_skip_stage("outline", {})
        assert skip is False

        skip, reason = workflow.should_skip_stage("write", {})
        assert skip is False


class TestDocumentGenerationLLMCalls:
    """Tests for LLM call handling."""

    def test_get_client_no_api_key(self):
        """Test client returns None without API key."""
        workflow = DocumentGenerationWorkflow()
        workflow._api_key = None

        client = workflow._get_client()

        assert client is None

    @pytest.mark.asyncio
    async def test_call_llm_no_client(self):
        """Test LLM call returns simulation when no client."""
        workflow = DocumentGenerationWorkflow()
        workflow._api_key = None

        content, input_tokens, output_tokens = await workflow._call_llm(
            ModelTier.CAPABLE, "System", "Generate documentation"
        )

        assert "[Simulated" in content
        assert input_tokens > 0

    @pytest.mark.asyncio
    async def test_call_llm_with_client(self):
        """Test LLM call with mocked client."""
        workflow = DocumentGenerationWorkflow()
        workflow._api_key = "test-key"  # pragma: allowlist secret

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Generated docs")]
        mock_response.usage.input_tokens = 200
        mock_response.usage.output_tokens = 100
        mock_client.messages.create.return_value = mock_response

        with patch.object(workflow, "_get_client", return_value=mock_client):
            content, input_tokens, output_tokens = await workflow._call_llm(
                ModelTier.CAPABLE, "System", "Message"
            )

        assert content == "Generated docs"
        assert input_tokens == 200
        assert output_tokens == 100


class TestFormatDocGenReport:
    """Tests for report formatting."""

    def test_format_report_basic(self):
        """Test basic report formatting."""
        result = {
            "document": "# API Reference\n\n## Introduction\n\nContent here...",
            "doc_type": "api_reference",
            "audience": "developers",
            "model_tier_used": "premium",
        }
        input_data = {"outline": "1. Introduction\n2. Usage"}

        report = format_doc_gen_report(result, input_data)

        assert "DOCUMENTATION GENERATION REPORT" in report
        assert "Api Reference" in report
        assert "Developers" in report
        assert "GENERATED DOCUMENTATION" in report

    def test_format_report_with_chunked_generation(self):
        """Test report with chunked generation info."""
        result = {
            "document": "Content",
            "doc_type": "guide",
            "audience": "users",
            "model_tier_used": "premium",
        }
        input_data = {
            "outline": "1. Intro",
            "chunked": True,
            "chunk_count": 3,
            "chunks_completed": 3,
        }

        report = format_doc_gen_report(result, input_data)

        assert "Chunked" in report
        assert "3 chunks" in report

    def test_format_report_with_warning(self):
        """Test report with warning message."""
        result = {
            "document": "Partial content",
            "doc_type": "guide",
            "audience": "users",
            "model_tier_used": "capable",
        }
        input_data = {
            "outline": "1. Intro",
            "warning": "Cost limit reached",
            "stopped_early": True,
        }

        report = format_doc_gen_report(result, input_data)

        assert "WARNING" in report
        assert "Cost limit reached" in report

    def test_format_report_with_export_path(self):
        """Test report with export path info."""
        result = {
            "document": "Content",
            "doc_type": "guide",
            "audience": "users",
            "model_tier_used": "premium",
            "export_path": "/docs/generated/guide.md",
            "report_path": "/docs/generated/guide_report.txt",
        }
        input_data = {"outline": "1. Intro"}

        report = format_doc_gen_report(result, input_data)

        assert "FILE EXPORT" in report
        assert "/docs/generated/guide.md" in report


class TestDocumentGenerationIntegration:
    """Integration tests for DocumentGenerationWorkflow."""

    @pytest.mark.asyncio
    async def test_full_workflow_simulation(self):
        """Test simulated full workflow execution."""
        with tempfile.TemporaryDirectory() as tmpdir:
            workflow = DocumentGenerationWorkflow(export_path=tmpdir)
            workflow._api_key = None  # Use simulation mode

            # Mock all LLM calls
            with patch.object(workflow, "_call_llm", new_callable=AsyncMock) as mock:
                mock.side_effect = [
                    ("1. Introduction\n2. Setup\n3. Usage", 100, 50),  # outline
                    ("# Introduction\n\nContent...\n\n# Setup\n\nMore...", 200, 1500),  # write
                    ("# Polished Introduction\n\n...", 300, 200),  # polish
                ]

                # Run outline stage
                outline_result, _, _ = await workflow._outline(
                    {
                        "source_code": "def example(): pass",
                        "doc_type": "api_reference",
                        "audience": "developers",
                    },
                    ModelTier.CHEAP,
                )

                # Run write stage
                write_result, _, _ = await workflow._write(
                    outline_result,
                    ModelTier.CAPABLE,
                )

                # Run polish stage
                polish_result, _, _ = await workflow._polish(
                    write_result,
                    ModelTier.PREMIUM,
                )

                assert "document" in polish_result
                assert "formatted_report" in polish_result

    @pytest.mark.asyncio
    async def test_graceful_degradation_on_error(self):
        """Test graceful degradation when LLM call fails."""
        workflow = DocumentGenerationWorkflow(graceful_degradation=True, max_cost=100)

        call_count = 0

        async def failing_llm(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                raise Exception("API error")
            return ("Content", 100, 50)

        with patch.object(workflow, "_call_llm", new_callable=AsyncMock) as mock:
            mock.side_effect = failing_llm

            result, _, _ = await workflow._write_chunked(
                sections=["A", "B", "C", "D"],
                outline="outline",
                doc_type="guide",
                audience="users",
                content_to_document="source",
                tier=ModelTier.CAPABLE,
            )

            # Should have partial results
            assert result["stopped_early"] is True
            assert "draft_document" in result
