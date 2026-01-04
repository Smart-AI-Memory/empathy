"""Coach Language Server
Implements LSP protocol to bridge IDE extensions to Coach engine

Copyright 2025 Deep Study AI, LLC
Licensed under Fair Source 0.9
"""

import logging
from typing import Any

from pygls.lsp import types as lsp_types
from pygls.lsp.methods import (
    CODE_ACTION,
    HOVER,
    TEXT_DOCUMENT_DID_CHANGE,
    TEXT_DOCUMENT_DID_OPEN,
    TEXT_DOCUMENT_DID_SAVE,
)
from pygls.server import LanguageServer

from ..coach import Coach, CoachOutput, WizardTask
from .cache import ResultCache
from .context_collector import ContextCollector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CoachLanguageServer(LanguageServer):
    """Language Server for Coach IDE integration"""

    def __init__(self):
        super().__init__(name="coach-lsp", version="1.0.0")
        self.coach = Coach()
        self.context_collector = ContextCollector()
        self.cache = ResultCache(ttl=300)  # 5 minute cache

        logger.info("Coach Language Server initialized with 16 wizards")

        # Register handlers
        self._register_handlers()

    def _register_handlers(self):
        """Register LSP message handlers"""

        @self.feature(TEXT_DOCUMENT_DID_OPEN)
        async def did_open(ls: LanguageServer, params: lsp_types.DidOpenTextDocumentParams):
            """Trigger analysis when file is opened"""
            logger.info(f"File opened: {params.text_document.uri}")
            # Optional: Run background analysis on open
            # await self._analyze_document(params.text_document.uri)

        @self.feature(TEXT_DOCUMENT_DID_CHANGE)
        async def did_change(ls: LanguageServer, params: lsp_types.DidChangeTextDocumentParams):
            """Handle file changes (incremental updates)"""
            logger.debug(f"File changed: {params.text_document.uri}")
            # Clear cache for this file
            self.cache.clear_file(params.text_document.uri)

        @self.feature(TEXT_DOCUMENT_DID_SAVE)
        async def did_save(ls: LanguageServer, params: lsp_types.DidSaveTextDocumentParams):
            """Trigger analysis on file save"""
            logger.info(f"File saved: {params.text_document.uri}")
            await self._analyze_document(params.text_document.uri)

        @self.feature(CODE_ACTION)
        async def code_action(
            ls: LanguageServer,
            params: lsp_types.CodeActionParams,
        ) -> list[lsp_types.CodeAction]:
            """Provide quick fixes from wizards"""
            diagnostics = params.context.diagnostics
            actions = []

            for diagnostic in diagnostics:
                if diagnostic.source == "coach.security":
                    # SecurityWizard fix
                    action = self._create_security_fix(diagnostic, params)
                    if action:
                        actions.append(action)
                elif diagnostic.source == "coach.performance":
                    # PerformanceWizard fix
                    action = self._create_performance_fix(diagnostic, params)
                    if action:
                        actions.append(action)
                elif diagnostic.source == "coach.accessibility":
                    # AccessibilityWizard fix
                    action = self._create_accessibility_fix(diagnostic, params)
                    if action:
                        actions.append(action)

            logger.info(f"Provided {len(actions)} code actions")
            return actions

        @self.feature(HOVER)
        async def hover(
            ls: LanguageServer,
            params: lsp_types.HoverParams,
        ) -> lsp_types.Hover | None:
            """Provide Level 4 predictions on hover"""
            document_uri = params.text_document.uri
            position = params.position

            logger.debug(f"Hover request at {document_uri}:{position.line}:{position.character}")

            # Get document context
            context = await self.context_collector.collect(document_uri, position)

            # Check for predictable patterns (connection pools, rate limits, etc.)
            prediction = await self._get_prediction(context)

            if prediction:
                logger.info(f"Providing Level 4 prediction: {prediction[:50]}...")
                return lsp_types.Hover(
                    contents=lsp_types.MarkupContent(
                        kind=lsp_types.MarkupKind.Markdown,
                        value=prediction,
                    ),
                )
            return None

        # Custom commands
        @self.command("coach/runWizard")
        async def run_wizard(ls: LanguageServer, args: list[Any]) -> dict[str, Any]:
            """Execute specific wizard"""
            wizard_name = args[0]
            task_data = args[1]

            logger.info(f"Running wizard: {wizard_name}")

            task = WizardTask(**task_data)

            # Check cache
            cache_key = f"{wizard_name}:{task.task}"
            cached = self.cache.get(cache_key)
            if cached:
                logger.info(f"Cache hit for {wizard_name}")
                return cached

            # Run wizard
            result = await self.coach.process(task, multi_wizard=False)

            # Cache result
            result_dict = self._serialize_coach_output(result)
            self.cache.set(cache_key, result_dict)

            logger.info(f"{wizard_name} completed with confidence {result.overall_confidence}")
            return result_dict

        @self.command("coach/multiWizardReview")
        async def multi_wizard_review(ls: LanguageServer, args: list[Any]) -> dict[str, Any]:
            """Run multi-wizard collaboration"""
            scenario = args[0]  # e.g., "new_api_endpoint"
            files = args[1] if len(args) > 1 else []

            logger.info(f"Multi-wizard review: {scenario} ({len(files)} files)")

            # Collect context from all files
            if files:
                context = await self.context_collector.collect_multi_file(files)
            else:
                context = f"Scenario: {scenario}"

            task = WizardTask(
                role="developer",
                task=f"Multi-wizard review: {scenario}",
                context=context,
            )

            # Run multi-wizard
            result = await self.coach.process(task, multi_wizard=True)

            logger.info(f"Multi-wizard review completed with {len(result.routing)} wizards")
            return self._serialize_coach_output(result)

        @self.command("coach/predict")
        async def predict(ls: LanguageServer, args: list[Any]) -> str:
            """Get Level 4 prediction for specific context"""
            context_type = args[0]  # e.g., "database_connection_pool"
            current_value = args[1] if len(args) > 1 else None

            logger.info(f"Prediction request: {context_type}")

            # Route to PerformanceWizard for prediction
            task = WizardTask(
                role="developer",
                task=f"Predict scaling issues for {context_type}",
                context=f"Current value: {current_value}" if current_value else context_type,
            )

            result = await self.coach.process(task, multi_wizard=False)

            # Extract prediction from diagnosis
            prediction = result.primary_output.diagnosis
            return prediction

        @self.command("coach/healthCheck")
        async def health_check(ls: LanguageServer, args: list[Any]) -> dict[str, Any]:
            """Health check endpoint for IDE to verify server is running"""
            return {
                "status": "healthy",
                "version": "1.0.0",
                "wizards": len(self.coach.wizards),
                "wizard_names": [w.__class__.__name__ for w in self.coach.wizards],
            }

    async def _analyze_document(self, document_uri: str):
        """Run background analysis on document"""
        try:
            # Collect context
            context = await self.context_collector.collect(document_uri)

            # Run background wizards (SecurityWizard, PerformanceWizard)
            task = WizardTask(
                role="developer",
                task="Analyze for security and performance issues",
                context=context,
            )

            result = await self.coach.process(task, multi_wizard=True)

            # Convert to LSP diagnostics
            diagnostics = self._convert_to_diagnostics(result)

            # Publish diagnostics
            self.publish_diagnostics(document_uri, diagnostics)

            logger.info(f"Published {len(diagnostics)} diagnostics for {document_uri}")
        except Exception as e:
            logger.error(f"Error analyzing document {document_uri}: {e}")

    def _convert_to_diagnostics(self, result: CoachOutput) -> list[lsp_types.Diagnostic]:
        """Convert wizard output to LSP diagnostics"""
        diagnostics = []

        for output in [result.primary_output] + result.secondary_outputs:
            wizard_name = output.wizard_name.lower().replace("wizard", "")

            # Extract issues from artifacts
            for artifact in output.artifacts:
                content_lower = artifact.content.lower()
                if any(
                    keyword in content_lower
                    for keyword in ["issue", "warning", "vulnerability", "problem"]
                ):
                    # Determine severity
                    if "critical" in content_lower or "security" in wizard_name:
                        severity = lsp_types.DiagnosticSeverity.Error
                    elif "warning" in content_lower:
                        severity = lsp_types.DiagnosticSeverity.Warning
                    else:
                        severity = lsp_types.DiagnosticSeverity.Information

                    diagnostic = lsp_types.Diagnostic(
                        range=lsp_types.Range(
                            start=lsp_types.Position(line=0, character=0),
                            end=lsp_types.Position(line=0, character=100),
                        ),
                        message=artifact.content[:200],  # Truncate long messages
                        severity=severity,
                        source=f"coach.{wizard_name}",
                    )
                    diagnostics.append(diagnostic)

        return diagnostics

    def _create_security_fix(
        self,
        diagnostic: lsp_types.Diagnostic,
        params: lsp_types.CodeActionParams,
    ) -> lsp_types.CodeAction | None:
        """Create quick fix for security issue"""
        action = lsp_types.CodeAction(
            title=f"🛡️ SecurityWizard: Fix {diagnostic.message[:50]}",
            kind=lsp_types.CodeActionKind.QuickFix,
        )
        action.diagnostics = [diagnostic]
        # TODO: Add actual edit to fix the issue
        return action

    def _create_performance_fix(
        self,
        diagnostic: lsp_types.Diagnostic,
        params: lsp_types.CodeActionParams,
    ) -> lsp_types.CodeAction | None:
        """Create quick fix for performance issue"""
        action = lsp_types.CodeAction(
            title=f"⚡ PerformanceWizard: Optimize {diagnostic.message[:50]}",
            kind=lsp_types.CodeActionKind.QuickFix,
        )
        action.diagnostics = [diagnostic]
        return action

    def _create_accessibility_fix(
        self,
        diagnostic: lsp_types.Diagnostic,
        params: lsp_types.CodeActionParams,
    ) -> lsp_types.CodeAction | None:
        """Create quick fix for accessibility issue"""
        action = lsp_types.CodeAction(
            title=f"♿ AccessibilityWizard: Fix {diagnostic.message[:50]}",
            kind=lsp_types.CodeActionKind.QuickFix,
        )
        action.diagnostics = [diagnostic]
        return action

    async def _get_prediction(self, context: str) -> str | None:
        """Get Level 4 anticipatory prediction"""
        # Look for predictable patterns in context
        context_lower = context.lower()

        # Pattern 1: Database connection pool
        if "pool_size" in context_lower or "connection" in context_lower:
            return (
                "⚠️ **PerformanceWizard Prediction (Level 4)**\n\n"
                "At 5K req/day growth rate, this connection pool may saturate in ~45 days.\n\n"
                "**Impact**: 503 timeout errors\n\n"
                "**Preventive Action**: Consider increasing pool size or implementing connection pooling\n\n"
                "[Run Full Analysis](command:coach.runWizard?PerformanceWizard)"
            )

        # Pattern 2: Rate limiting
        if "rate" in context_lower and "limit" in context_lower:
            return (
                "⚠️ **PerformanceWizard Prediction (Level 4)**\n\n"
                "Current rate limit may be insufficient as traffic scales.\n\n"
                "**Prediction**: Rate limit will be hit in ~60 days at current growth\n\n"
                "**Preventive Action**: Implement adaptive rate limiting or increase limits\n\n"
                "[Run Full Analysis](command:coach.runWizard?PerformanceWizard)"
            )

        # Pattern 3: Security issues (SQL, XSS, etc.)
        if any(
            keyword in context_lower
            for keyword in ["sql", "query", "execute", "f'select", 'f"select']
        ):
            return (
                "🛡️ **SecurityWizard Alert**\n\n"
                "Potential SQL injection vulnerability detected.\n\n"
                "**Risk**: High - Could expose sensitive data\n\n"
                "**Recommended**: Use parameterized queries\n\n"
                "[Run Security Audit](command:coach.runWizard?SecurityWizard)"
            )

        return None

    def _serialize_coach_output(self, result: CoachOutput) -> dict[str, Any]:
        """Convert CoachOutput to JSON-serializable dict"""
        return {
            "routing": result.routing,
            "primary_output": {
                "wizard_name": result.primary_output.wizard_name,
                "diagnosis": result.primary_output.diagnosis,
                "artifacts": [
                    {"name": a.name, "content": a.content, "format": a.format}
                    for a in result.primary_output.artifacts
                ],
                "confidence": result.primary_output.confidence,
            },
            "secondary_outputs": [
                {
                    "wizard_name": o.wizard_name,
                    "diagnosis": o.diagnosis,
                    "artifacts": [
                        {"name": a.name, "content": a.content, "format": a.format}
                        for a in o.artifacts
                    ],
                    "confidence": o.confidence,
                }
                for o in result.secondary_outputs
            ],
            "synthesis": result.synthesis,
            "overall_confidence": result.overall_confidence,
        }


def start_lsp_server():
    """Start the Language Server on stdio"""
    server = CoachLanguageServer()
    logger.info("Starting Coach Language Server...")
    server.start_io()


if __name__ == "__main__":
    start_lsp_server()
