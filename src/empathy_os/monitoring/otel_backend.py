"""OpenTelemetry Backend for LLM Telemetry

Exports telemetry data to OTEL-compatible collectors (SigNoz, Datadog, New Relic).

**Features:**
- Auto-detection of OTEL collector (localhost:4317)
- Environment variable configuration (EMPATHY_OTEL_ENDPOINT)
- Semantic conventions for LLM traces
- Batch export with retry logic
- Graceful fallback if collector unavailable

**Setup:**
```bash
export EMPATHY_OTEL_ENDPOINT=http://localhost:4317
pip install empathy-framework[otel]
```

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import os
import socket

from empathy_os.models.telemetry import LLMCallRecord, WorkflowRunRecord


class OTELBackend:
    """OpenTelemetry backend for exporting telemetry to OTEL collectors.

    Implements the TelemetryBackend protocol for OTEL export.

    **Auto-detection:**
    - Checks for OTEL collector on localhost:4317
    - Falls back to EMPATHY_OTEL_ENDPOINT environment variable

    **Semantic Conventions:**
    - LLM calls → OTEL spans with llm.* attributes
    - Workflows → OTEL traces with workflow.* attributes

    **Batch Export:**
    - Buffers records and exports in batches
    - Retries on transient failures
    - Logs errors but doesn't crash

    Example:
        >>> backend = OTELBackend()
        >>> if backend.is_available():
        ...     backend.log_call(call_record)
        ...     backend.log_workflow(workflow_record)
    """

    def __init__(
        self,
        endpoint: str | None = None,
        batch_size: int = 10,
        retry_count: int = 3,
    ):
        """Initialize OTEL backend.

        Args:
            endpoint: OTEL collector endpoint (default: auto-detect)
            batch_size: Number of records to buffer before export
            retry_count: Number of retries on transient failures
        """
        self.endpoint = endpoint or self._detect_endpoint()
        self.batch_size = batch_size
        self.retry_count = retry_count
        self.call_buffer: list[LLMCallRecord] = []
        self.workflow_buffer: list[WorkflowRunRecord] = []
        self._available = self._check_availability()

        # Try importing OTEL dependencies
        self._otel_available = self._check_otel_installed()

        if self._otel_available and self._available:
            self._init_otel()

    def _detect_endpoint(self) -> str:
        """Detect OTEL collector endpoint.

        Checks (in order):
        1. EMPATHY_OTEL_ENDPOINT environment variable
        2. localhost:4317 (default OTEL gRPC port)

        Returns:
            OTEL collector endpoint URL
        """
        # Check environment variable
        endpoint = os.getenv("EMPATHY_OTEL_ENDPOINT")
        if endpoint:
            return endpoint

        # Check localhost:4317
        if self._is_port_open("localhost", 4317):
            return "http://localhost:4317"

        # Default (will fail availability check)
        return "http://localhost:4317"

    def _is_port_open(self, host: str, port: int, timeout: float = 1.0) -> bool:
        """Check if a port is open on a host.

        Args:
            host: Hostname or IP address
            port: Port number
            timeout: Connection timeout in seconds

        Returns:
            True if port is open, False otherwise
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((host, port))
            sock.close()
            return True
        except (TimeoutError, OSError):
            return False

    def _check_availability(self) -> bool:
        """Check if OTEL collector is available.

        Returns:
            True if collector is reachable, False otherwise
        """
        if not self.endpoint:
            return False

        # Parse endpoint to extract host and port
        try:
            # Remove http:// or https://
            endpoint = self.endpoint.replace("http://", "").replace("https://", "")
            if ":" in endpoint:
                host, port_str = endpoint.split(":")
                port = int(port_str.split("/")[0])  # Remove any path
            else:
                host = endpoint
                port = 4317  # Default OTEL gRPC port

            return self._is_port_open(host, port)
        except (ValueError, IndexError):
            return False

    def _check_otel_installed(self) -> bool:
        """Check if OTEL dependencies are installed.

        Returns:
            True if opentelemetry-api and opentelemetry-sdk are installed
        """
        try:
            import opentelemetry.trace  # noqa: F401
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
                OTLPSpanExporter,  # noqa: F401
            )
            from opentelemetry.sdk.trace import TracerProvider  # noqa: F401
            from opentelemetry.sdk.trace.export import BatchSpanProcessor  # noqa: F401

            return True
        except ImportError:
            return False

    def _init_otel(self) -> None:
        """Initialize OTEL tracer and exporter."""
        try:
            from opentelemetry import trace
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
            from opentelemetry.sdk.resources import Resource
            from opentelemetry.sdk.trace import TracerProvider
            from opentelemetry.sdk.trace.export import BatchSpanProcessor

            # Create resource with service name
            resource = Resource.create(
                {
                    "service.name": "empathy-framework",
                    "service.version": "3.8.0-alpha",
                }
            )

            # Create tracer provider
            provider = TracerProvider(resource=resource)

            # Create OTLP exporter
            exporter = OTLPSpanExporter(endpoint=self.endpoint, insecure=True)

            # Add batch processor
            processor = BatchSpanProcessor(exporter)
            provider.add_span_processor(processor)

            # Set global tracer provider
            trace.set_tracer_provider(provider)

            # Get tracer
            self.tracer = trace.get_tracer("empathy.llm.telemetry", "3.8.0-alpha")

        except Exception as e:
            print(f"⚠️  Failed to initialize OTEL: {e}")
            self._available = False

    def is_available(self) -> bool:
        """Check if OTEL backend is available.

        Returns:
            True if OTEL collector is reachable and dependencies installed
        """
        return self._available and self._otel_available

    def log_call(self, record: LLMCallRecord) -> None:
        """Log an LLM call record to OTEL.

        Creates an OTEL span with LLM semantic conventions.

        Args:
            record: LLM call record to log
        """
        if not self.is_available():
            return

        try:
            # Create span with LLM semantic conventions
            with self.tracer.start_as_current_span(
                f"llm.{record.provider}.{record.model_id}"
            ) as span:
                # Set standard LLM attributes
                span.set_attribute("llm.provider", record.provider)
                span.set_attribute("llm.model", record.model_id)
                span.set_attribute("llm.tier", record.tier)
                span.set_attribute("llm.task_type", record.task_type)

                # Set token usage
                span.set_attribute("llm.usage.input_tokens", record.input_tokens)
                span.set_attribute("llm.usage.output_tokens", record.output_tokens)
                span.set_attribute(
                    "llm.usage.total_tokens", record.input_tokens + record.output_tokens
                )

                # Set cost and latency
                span.set_attribute("llm.cost.estimated", record.estimated_cost)
                if record.actual_cost:
                    span.set_attribute("llm.cost.actual", record.actual_cost)
                span.set_attribute("llm.latency_ms", record.latency_ms)

                # Set workflow context
                if record.workflow_name:
                    span.set_attribute("workflow.name", record.workflow_name)
                if record.step_name:
                    span.set_attribute("workflow.step", record.step_name)
                if record.session_id:
                    span.set_attribute("session.id", record.session_id)

                # Set fallback info
                if record.fallback_used:
                    span.set_attribute("llm.fallback.used", True)
                    if record.original_provider:
                        span.set_attribute(
                            "llm.fallback.original_provider", record.original_provider
                        )
                    if record.original_model:
                        span.set_attribute("llm.fallback.original_model", record.original_model)

                # Set error info
                if not record.success:
                    span.set_attribute("llm.error", True)
                    if record.error_type:
                        span.set_attribute("llm.error.type", record.error_type)
                    if record.error_message:
                        span.set_attribute("llm.error.message", record.error_message)

        except Exception as e:
            print(f"⚠️  Failed to export LLM call to OTEL: {e}")

    def log_workflow(self, record: WorkflowRunRecord) -> None:
        """Log a workflow run record to OTEL.

        Creates an OTEL trace with workflow semantic conventions.

        Args:
            record: Workflow run record to log
        """
        if not self.is_available():
            return

        try:
            # Create trace for workflow
            with self.tracer.start_as_current_span(f"workflow.{record.workflow_name}") as span:
                # Set workflow attributes
                span.set_attribute("workflow.name", record.workflow_name)
                span.set_attribute("workflow.run_id", record.run_id)
                if record.session_id:
                    span.set_attribute("session.id", record.session_id)

                # Set token usage
                span.set_attribute("workflow.usage.input_tokens", record.total_input_tokens)
                span.set_attribute("workflow.usage.output_tokens", record.total_output_tokens)
                span.set_attribute(
                    "workflow.usage.total_tokens",
                    record.total_input_tokens + record.total_output_tokens,
                )

                # Set cost and savings
                span.set_attribute("workflow.cost.total", record.total_cost)
                span.set_attribute("workflow.cost.baseline", record.baseline_cost)
                span.set_attribute("workflow.cost.savings", record.savings)
                span.set_attribute("workflow.cost.savings_percent", record.savings_percent)

                # Set duration
                span.set_attribute("workflow.duration_ms", record.total_duration_ms)

                # Set providers and tiers used
                span.set_attribute("workflow.providers_used", ",".join(record.providers_used))
                span.set_attribute("workflow.tiers_used", ",".join(record.tiers_used))

                # Set success status
                span.set_attribute("workflow.success", record.success)
                if not record.success and record.error:
                    span.set_attribute("workflow.error", record.error)

                # Create child spans for each stage
                for stage in record.stages:
                    with self.tracer.start_as_current_span(
                        f"stage.{stage.stage_name}"
                    ) as stage_span:
                        stage_span.set_attribute("stage.name", stage.stage_name)
                        stage_span.set_attribute("llm.tier", stage.tier)
                        stage_span.set_attribute("llm.model", stage.model_id)
                        stage_span.set_attribute("llm.usage.input_tokens", stage.input_tokens)
                        stage_span.set_attribute("llm.usage.output_tokens", stage.output_tokens)
                        stage_span.set_attribute("llm.cost", stage.cost)
                        stage_span.set_attribute("llm.latency_ms", stage.latency_ms)
                        stage_span.set_attribute("stage.success", stage.success)

                        if stage.skipped:
                            stage_span.set_attribute("stage.skipped", True)
                            if stage.skip_reason:
                                stage_span.set_attribute("stage.skip_reason", stage.skip_reason)

                        if stage.error:
                            stage_span.set_attribute("stage.error", stage.error)

        except Exception as e:
            print(f"⚠️  Failed to export workflow to OTEL: {e}")

    def flush(self) -> None:
        """Flush any buffered records to OTEL collector.

        Called automatically on shutdown or can be called manually.
        """
        if not self.is_available():
            return

        try:
            from opentelemetry import trace

            # Get tracer provider and force flush
            provider = trace.get_tracer_provider()
            if hasattr(provider, "force_flush"):
                provider.force_flush()
        except Exception as e:
            print(f"⚠️  Failed to flush OTEL data: {e}")

    def __del__(self) -> None:
        """Cleanup on deletion."""
        self.flush()
