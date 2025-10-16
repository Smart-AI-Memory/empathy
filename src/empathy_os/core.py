"""
EmpathyOS - Core Implementation

The main entry point for the Empathy Framework, providing access to all
5 empathy levels and system thinking integrations.

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
import logging

from .emergence import EmergenceDetector
from .exceptions import ValidationError, ConfidenceThresholdError
from .feedback_loops import FeedbackLoopDetector
from .leverage_points import LeveragePointAnalyzer, LeveragePoint


@dataclass
class CollaborationState:
    """
    Stock & Flow model of AI-human collaboration

    Tracks:
    - Trust level (stock that accumulates/erodes)
    - Shared context (accumulated understanding)
    - Success/failure rates (quality metrics)
    - Flow rates (how fast trust builds/erodes)
    """

    # Stocks (accumulate over time)
    trust_level: float = 0.5  # 0.0 to 1.0, start neutral
    shared_context: Dict = field(default_factory=dict)
    successful_interventions: int = 0
    failed_interventions: int = 0

    # Flow rates (change stocks per interaction)
    trust_building_rate: float = 0.05  # Per successful interaction
    trust_erosion_rate: float = 0.10  # Per failed interaction (erosion faster)
    context_accumulation_rate: float = 0.1

    # Metadata
    session_start: datetime = field(default_factory=datetime.now)
    total_interactions: int = 0
    trust_trajectory: List[float] = field(default_factory=list)  # Historical trust levels

    def update_trust(self, outcome: str):
        """Update trust stock based on interaction outcome"""
        if outcome == "success":
            self.trust_level += self.trust_building_rate
            self.successful_interventions += 1
        elif outcome == "failure":
            self.trust_level -= self.trust_erosion_rate
            self.failed_interventions += 1

        # Clamp to [0, 1]
        self.trust_level = max(0.0, min(1.0, self.trust_level))
        self.total_interactions += 1

        # Track trajectory
        self.trust_trajectory.append(self.trust_level)


class EmpathyOS:
    """
    Empathy Operating System for AI-Human Collaboration

    Integrates:
    - 5-level Empathy Maturity Model
    - Systems Thinking (feedback loops, emergence, leverage points)
    - Tactical Empathy (Voss)
    - Emotional Intelligence (Goleman)
    - Clear Thinking (Naval)

    Goal: Enable AI to operate at Levels 3-4 (Proactive/Anticipatory)

    Example:
        >>> empathy = EmpathyOS(user_id="developer_123", target_level=4)
        >>> result = await empathy.level_4_anticipatory(system_trajectory)
        >>> print(result["bottlenecks_predicted"])
    """

    def __init__(
        self,
        user_id: str,
        target_level: int = 3,
        confidence_threshold: float = 0.75,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize EmpathyOS

        Args:
            user_id: Unique identifier for user/team
            target_level: Target empathy level (1-5), default 3 (Proactive)
            confidence_threshold: Minimum confidence for anticipatory actions (0.0-1.0)
            logger: Optional logger instance for structured logging
        """
        self.user_id = user_id
        self.target_level = target_level
        self.confidence_threshold = confidence_threshold
        self.logger = logger or logging.getLogger(__name__)

        # Collaboration state tracking
        self.collaboration_state = CollaborationState()

        # System thinking components
        self.feedback_detector = FeedbackLoopDetector()
        self.emergence_detector = EmergenceDetector()
        self.leverage_analyzer = LeveragePointAnalyzer()

        # Pattern storage for Level 3+
        self.user_patterns: List[Dict] = []
        self.system_trajectory: List[Dict] = []

        # Current empathy level
        self.current_empathy_level = 1

    async def __aenter__(self):
        """
        Enter async context manager

        Enables usage: async with EmpathyOS(...) as empathy:

        Returns:
            self: The EmpathyOS instance
        """
        # Initialize any async resources here if needed
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Exit async context manager

        Performs cleanup when exiting the context:
        - Saves patterns if persistence is enabled
        - Closes any open connections
        - Logs final collaboration state

        Args:
            exc_type: Exception type if an exception occurred
            exc_val: Exception value if an exception occurred
            exc_tb: Exception traceback if an exception occurred

        Returns:
            False to propagate exceptions (standard behavior)
        """
        await self._cleanup()
        return False  # Don't suppress exceptions

    async def _cleanup(self):
        """
        Cleanup resources on context exit

        **Extension Point**: Override to add custom cleanup logic
        (e.g., save state to database, close connections, send metrics)
        """
        # Future: Save patterns to disk
        # Future: Send final metrics
        # Future: Close async connections
        pass

    # =========================================================================
    # LEVEL 1: REACTIVE EMPATHY
    # =========================================================================

    async def level_1_reactive(self, user_request: str) -> Dict:
        """
        Level 1: Reactive Empathy

        Respond to explicit request accurately and helpfully.
        No anticipation, no proactive action.

        Args:
            user_request: User's explicit request

        Returns:
            Dict with result and reasoning

        Raises:
            ValueError: If user_request is empty or not a string
        """
        # Input validation
        if not isinstance(user_request, str):
            raise ValidationError(f"user_request must be a string, got {type(user_request).__name__}")
        if not user_request.strip():
            raise ValidationError("user_request cannot be empty")

        self.logger.info("Level 1 reactive request started", extra={
            "user_id": self.user_id,
            "empathy_level": 1,
            "request_length": len(user_request)
        })

        self.current_empathy_level = 1

        # Process request (implement your domain logic here)
        result = await self._process_request(user_request)

        self.logger.info("Level 1 reactive request completed", extra={
            "user_id": self.user_id,
            "success": result.get("status") == "success"
        })

        # Update collaboration state
        self.collaboration_state.total_interactions += 1

        return {
            "level": 1,
            "type": "reactive",
            "result": result,
            "reasoning": "Responding to explicit request",
            "empathy_level": "Reactive: Help after being asked",
        }

    # =========================================================================
    # LEVEL 2: GUIDED EMPATHY
    # =========================================================================

    async def level_2_guided(self, user_request: str) -> Dict:
        """
        Level 2: Guided Empathy

        Use calibrated questions (Voss) to clarify intent before acting.
        Collaborative exploration to uncover hidden needs.

        Args:
            user_request: User's request (potentially ambiguous)

        Returns:
            Dict with clarification questions or refined result

        Raises:
            ValueError: If user_request is empty or not a string
        """
        # Input validation
        if not isinstance(user_request, str):
            raise ValidationError(f"user_request must be a string, got {type(user_request).__name__}")
        if not user_request.strip():
            raise ValidationError("user_request cannot be empty")

        self.current_empathy_level = 2

        self.logger.info("Level 2 guided request started", extra={
            "user_id": self.user_id,
            "empathy_level": 2,
            "request_length": len(user_request)
        })

        # Use Voss's calibrated questions
        clarification = await self._ask_calibrated_questions(user_request)

        if clarification["needs_clarification"]:
            return {
                "level": 2,
                "type": "guided",
                "action": "clarify_first",
                "questions": clarification["questions"],
                "reasoning": "Asking clarifying questions to understand true intent",
                "empathy_level": "Guided: Collaborative exploration",
            }

        # Refine request based on clarification
        refined_request = self._refine_request(user_request, clarification)

        # Process refined request
        result = await self._process_request(refined_request)

        # Update collaboration state
        self.collaboration_state.total_interactions += 1
        self.collaboration_state.shared_context.update(clarification)

        self.logger.info("Level 2 guided request completed", extra={
            "user_id": self.user_id,
            "empathy_level": 2,
            "action": "proceed",
            "clarification_applied": True
        })

        return {
            "level": 2,
            "type": "guided",
            "action": "proceed",
            "result": result,
            "clarification": clarification,
            "reasoning": "Collaborated to refine understanding before execution",
            "empathy_level": "Guided: Clarified through questions",
        }

    # =========================================================================
    # LEVEL 3: PROACTIVE EMPATHY
    # =========================================================================

    async def level_3_proactive(self, context: Dict) -> Dict:
        """
        Level 3: Proactive Empathy

        Detect patterns, act on leading indicators.
        Take initiative without being asked.

        Args:
            context: Current context (user activity, system state, etc.)

        Returns:
            Dict with proactive actions taken

        Raises:
            ValueError: If context is not a dict or is empty
        """
        # Input validation
        if not isinstance(context, dict):
            raise ValidationError(f"context must be a dict, got {type(context).__name__}")
        if not context:
            raise ValidationError("context cannot be empty")

        self.current_empathy_level = 3

        self.logger.info("Level 3 proactive analysis started", extra={
            "user_id": self.user_id,
            "empathy_level": 3,
            "context_keys": list(context.keys())
        })

        # Detect current patterns
        active_patterns = self._detect_active_patterns(context)

        # Select proactive actions based on patterns
        proactive_actions = []

        for pattern in active_patterns:
            if pattern["confidence"] > 0.8:  # High confidence required
                action = self._design_proactive_action(pattern)

                # Safety check
                if self._is_safe_to_execute(action):
                    proactive_actions.append(action)

        # Execute proactive actions
        results = await self._execute_proactive_actions(proactive_actions)

        # Update collaboration state
        for result in results:
            outcome = "success" if result["success"] else "failure"
            self.collaboration_state.update_trust(outcome)

        self.logger.info("Level 3 proactive actions completed", extra={
            "user_id": self.user_id,
            "empathy_level": 3,
            "patterns_detected": len(active_patterns),
            "actions_taken": len(proactive_actions),
            "success_rate": sum(1 for r in results if r["success"]) / len(results) if results else 0
        })

        return {
            "level": 3,
            "type": "proactive",
            "patterns_detected": len(active_patterns),
            "actions_taken": len(proactive_actions),
            "results": results,
            "reasoning": "Acting on detected patterns without being asked",
            "empathy_level": "Proactive: Act before being asked",
        }

    # =========================================================================
    # LEVEL 4: ANTICIPATORY EMPATHY
    # =========================================================================

    async def level_4_anticipatory(self, system_trajectory: Dict) -> Dict:
        """
        Level 4: Anticipatory Empathy (THE INNOVATION)

        Predict future bottlenecks, design relief in advance.

        This is STRATEGIC CARE:
        - Timing + Prediction + Initiative
        - Solve tomorrow's pain today
        - Act without being told (but without overstepping)

        Args:
            system_trajectory: System state + growth trends + constraints

        Returns:
            Dict with predicted bottlenecks and interventions

        Raises:
            ValueError: If system_trajectory is not a dict or is empty
        """
        # Input validation
        if not isinstance(system_trajectory, dict):
            raise ValidationError(f"system_trajectory must be a dict, got {type(system_trajectory).__name__}")
        if not system_trajectory:
            raise ValidationError("system_trajectory cannot be empty")

        self.current_empathy_level = 4

        self.logger.info("Level 4 anticipatory prediction started", extra={
            "user_id": self.user_id,
            "empathy_level": 4,
            "trajectory_keys": list(system_trajectory.keys())
        })

        # Analyze system trajectory
        predicted_bottlenecks = self._predict_future_bottlenecks(system_trajectory)

        # Design structural relief for each bottleneck
        interventions = []

        for bottleneck in predicted_bottlenecks:
            # Only intervene if:
            # 1. High confidence (>75%)
            # 2. Appropriate time horizon (30-120 days)
            # 3. Reversible action
            if self._should_anticipate(bottleneck):
                intervention = self._design_anticipatory_intervention(bottleneck)
                interventions.append(intervention)

        # Execute anticipatory interventions
        results = await self._execute_anticipatory_interventions(interventions)

        # Update collaboration state
        for result in results:
            outcome = "success" if result["success"] else "failure"
            self.collaboration_state.update_trust(outcome)

        self.logger.info("Level 4 anticipatory interventions completed", extra={
            "user_id": self.user_id,
            "empathy_level": 4,
            "bottlenecks_predicted": len(predicted_bottlenecks),
            "interventions_executed": len(interventions),
            "success_rate": sum(1 for r in results if r["success"]) / len(results) if results else 0
        })

        return {
            "level": 4,
            "type": "anticipatory",
            "bottlenecks_predicted": predicted_bottlenecks,
            "interventions_designed": len(interventions),
            "results": results,
            "reasoning": "Predicting future bottlenecks and designing relief in advance",
            "empathy_level": "Anticipatory: Predict and prevent problems",
            "formula": "Timing + Prediction + Initiative = Anticipatory Empathy",
        }

    # =========================================================================
    # LEVEL 5: SYSTEMS EMPATHY
    # =========================================================================

    async def level_5_systems(self, domain_context: Dict) -> Dict:
        """
        Level 5: Systems Empathy

        Build structures that help at scale.
        Design leverage points, frameworks, self-sustaining systems.

        This is ARCHITECTURAL CARE:
        - One framework → infinite applications
        - Solve entire problem class, not individual instances
        - Design for emergence of desired properties

        Args:
            domain_context: Domain information, recurring problems, patterns

        Returns:
            Dict with designed frameworks and leverage points

        Raises:
            ValueError: If domain_context is not a dict or is empty
        """
        # Input validation
        if not isinstance(domain_context, dict):
            raise ValidationError(f"domain_context must be a dict, got {type(domain_context).__name__}")
        if not domain_context:
            raise ValidationError("domain_context cannot be empty")

        self.current_empathy_level = 5

        self.logger.info("Level 5 systems framework design started", extra={
            "user_id": self.user_id,
            "empathy_level": 5,
            "domain_keys": list(domain_context.keys())
        })

        # Identify problem class (not individual problem)
        problem_classes = self._identify_problem_classes(domain_context)

        # Find leverage points (Meadows's framework)
        leverage_points = []
        for problem_class in problem_classes:
            points = self.leverage_analyzer.find_leverage_points(problem_class)
            leverage_points.extend(points)

        # Design structural interventions at highest leverage points
        frameworks = []
        for lp in leverage_points:
            if lp.level.value >= 8:  # High leverage points only (Rules and above)
                framework = self._design_framework(lp)
                frameworks.append(framework)

        # Implement frameworks
        results = await self._implement_frameworks(frameworks)

        self.logger.info("Level 5 systems frameworks implemented", extra={
            "user_id": self.user_id,
            "empathy_level": 5,
            "problem_classes": len(problem_classes),
            "leverage_points_found": len(leverage_points),
            "frameworks_deployed": len(frameworks)
        })

        return {
            "level": 5,
            "type": "systems",
            "problem_classes": len(problem_classes),
            "leverage_points": leverage_points,
            "frameworks_designed": len(frameworks),
            "results": results,
            "reasoning": "Building structural solutions that scale to entire problem class",
            "empathy_level": "Systems: Build structures that help at scale",
        }

    # =========================================================================
    # HELPER METHODS (implement based on your domain)
    # =========================================================================

    async def _process_request(self, request: str) -> Dict:
        """
        Process user request (implement domain logic)

        **Extension Point**: Override this method in subclasses to implement
        your specific domain logic for processing user requests.

        Args:
            request: The user's request string

        Returns:
            Dict with processed result and status
        """
        # Placeholder - implement your actual request processing
        return {"processed": request, "status": "success"}

    async def _ask_calibrated_questions(self, request: str) -> Dict:
        """
        Voss's tactical empathy: Ask calibrated questions

        **Extension Point**: Override to implement sophisticated clarification
        logic using NLP, LLMs, or domain-specific heuristics.

        Args:
            request: The user's request string

        Returns:
            Dict with needs_clarification flag and optional questions list
        """
        # Simple heuristic - in production, use NLP/LLM
        needs_clarification = any(
            word in request.lower() for word in ["some", "a few", "many", "soon"]
        )

        if needs_clarification:
            return {
                "needs_clarification": True,
                "questions": [
                    "What are you hoping to accomplish?",
                    "How does this fit into your workflow?",
                    "What would make this most helpful right now?",
                ],
            }
        return {"needs_clarification": False}

    def _refine_request(self, original: str, clarification: Dict) -> str:
        """
        Refine request based on clarification responses

        **Extension Point**: Override to implement domain-specific request refinement
        based on clarification questions and user responses.

        Args:
            original: Original request string
            clarification: Dict containing clarification questions and responses

        Returns:
            Refined request string with added context
        """
        # If no clarification was needed, return original
        if not clarification.get("needs_clarification", False):
            return original

        # If clarification responses exist, incorporate them
        if "responses" in clarification:
            refinements = []
            for question, response in clarification["responses"].items():
                refinements.append(f"{question}: {response}")

            refined = f"{original}\n\nClarifications:\n" + "\n".join(f"- {r}" for r in refinements)
            return refined

        # Default: return original
        return original

    def _detect_active_patterns(self, context: Dict) -> List[Dict]:
        """Detect patterns in user behavior"""
        patterns = []

        # Example pattern detection logic
        if context.get("repeated_action"):
            patterns.append(
                {
                    "type": "sequential",
                    "pattern": "user_always_does_X_before_Y",
                    "confidence": 0.85,
                }
            )

        return patterns

    def _design_proactive_action(self, pattern: Dict) -> Dict:
        """Design proactive action based on pattern"""
        return {
            "action": "prefetch_data",
            "reasoning": f"Pattern detected: {pattern['pattern']}",
            "confidence": pattern["confidence"],
        }

    def _is_safe_to_execute(self, action: Dict) -> bool:
        """Safety check for proactive actions"""
        return action.get("confidence", 0) > 0.8

    async def _execute_proactive_actions(self, actions: List[Dict]) -> List[Dict]:
        """
        Execute proactive actions

        **Extension Point**: Override to implement actual execution of proactive
        actions in your domain (e.g., file operations, API calls, UI updates).

        This default implementation simulates execution with basic validation.
        Override this method to add real action execution logic.

        Args:
            actions: List of action dicts to execute

        Returns:
            List of result dicts with action and success status
        """
        results = []
        for action in actions:
            # Validate action has required fields
            if not action.get("action"):
                results.append({
                    "action": action,
                    "success": False,
                    "error": "Missing 'action' field"
                })
                continue

            # Log the action (in production, this would execute real logic)
            self.logger.debug(f"Executing proactive action: {action.get('action')}", extra={
                "user_id": self.user_id,
                "action_type": action.get("action"),
                "confidence": action.get("confidence", 0)
            })

            # Simulate successful execution
            results.append({
                "action": action,
                "success": True,
                "executed_at": datetime.now().isoformat()
            })

        return results

    def _predict_future_bottlenecks(self, trajectory: Dict) -> List[Dict]:
        """
        Predict where system will hit friction/overload

        Uses trajectory analysis, domain knowledge, historical patterns
        """
        bottlenecks = []

        # Example: Scaling bottleneck
        if trajectory.get("feature_count_increasing"):
            current = trajectory["current_feature_count"]
            growth_rate = trajectory.get("growth_rate", 0)
            projected_3mo = current + (growth_rate * 3)

            if projected_3mo > trajectory.get("threshold", 25):
                bottlenecks.append(
                    {
                        "type": "scaling_bottleneck",
                        "area": "testing",
                        "description": "Testing burden will become unsustainable",
                        "timeframe": "2-3 months",
                        "confidence": 0.75,
                        "current_state": f"{current} features",
                        "predicted_state": f"{projected_3mo} features",
                        "impact": trajectory.get("impact", "low"),
                    }
                )

        return bottlenecks

    def _should_anticipate(self, bottleneck: Dict) -> bool:
        """
        Safety checks for Level 4 anticipatory actions

        Validates:
        1. Confidence is above threshold
        2. Time horizon is appropriate (30-120 days)
        3. Impact justifies the intervention effort
        """
        # Check 1: Confidence threshold
        if bottleneck["confidence"] < self.confidence_threshold:
            return False

        # Check 2: Time horizon (30-120 days ideal)
        timeframe = bottleneck.get("timeframe", "")
        days = self._parse_timeframe_to_days(timeframe)

        # Too soon (<30 days) = reactive, not anticipatory
        # Too far (>120 days) = too uncertain to act on
        if days is not None and (days < 30 or days > 120):
            return False

        # Check 3: Impact justifies effort
        if bottleneck.get("impact", "low") not in ["high", "critical"]:
            return False

        return True

    def _parse_timeframe_to_days(self, timeframe: str) -> Optional[int]:
        """
        Parse timeframe string to days

        Examples:
            "2-3 months" -> 75 (midpoint)
            "60 days" -> 60
            "3 weeks" -> 21

        Returns:
            Number of days, or None if unparseable
        """
        import re

        if not timeframe:
            return None

        timeframe_lower = timeframe.lower()

        # Pattern: "X days"
        match = re.search(r'(\d+)\s*days?', timeframe_lower)
        if match:
            return int(match.group(1))

        # Pattern: "X weeks"
        match = re.search(r'(\d+)\s*weeks?', timeframe_lower)
        if match:
            return int(match.group(1)) * 7

        # Pattern: "X months" or "X-Y months"
        match = re.search(r'(\d+)(?:-(\d+))?\s*months?', timeframe_lower)
        if match:
            start = int(match.group(1))
            end = int(match.group(2)) if match.group(2) else start
            midpoint = (start + end) / 2
            return int(midpoint * 30)  # Approximate 30 days/month

        # Couldn't parse - return None (will skip time validation)
        return None

    def _design_anticipatory_intervention(self, bottleneck: Dict) -> Dict:
        """Design structural relief for predicted bottleneck"""
        return {
            "type": "framework_design",
            "target": bottleneck["area"],
            "deliverables": ["design_doc", "implementation_plan"],
            "timeline": "Implement before threshold",
        }

    async def _execute_anticipatory_interventions(
        self, interventions: List[Dict]
    ) -> List[Dict]:
        """
        Execute anticipatory interventions

        **Extension Point**: Override to implement actual execution of
        anticipatory interventions (e.g., scaling resources, provisioning
        infrastructure, preparing documentation).

        This default implementation simulates intervention execution with
        validation and logging. Override for real infrastructure changes.

        Args:
            interventions: List of intervention dicts to execute

        Returns:
            List of result dicts with intervention and success status
        """
        results = []
        for intervention in interventions:
            # Validate intervention has required fields
            if not intervention.get("type"):
                results.append({
                    "intervention": intervention,
                    "success": False,
                    "error": "Missing 'type' field"
                })
                continue

            # Log the intervention (in production, this would trigger real infrastructure changes)
            self.logger.info(f"Executing anticipatory intervention: {intervention.get('type')}", extra={
                "user_id": self.user_id,
                "intervention_type": intervention.get("type"),
                "target": intervention.get("target"),
                "timeline": intervention.get("timeline")
            })

            # Simulate successful intervention
            results.append({
                "intervention": intervention,
                "success": True,
                "executed_at": datetime.now().isoformat(),
                "status": "intervention_deployed"
            })

        return results

    def _identify_problem_classes(self, domain_context: Dict) -> List[Dict]:
        """
        Identify recurring problem classes (not individual instances)

        Use "Rule of Three":
        - Occurred at least 3 times
        - Will occur at least 3 more times
        - Affects at least 3 users/workflows
        """
        problem_classes = []

        # Example detection logic
        if domain_context.get("recurring_documentation_burden"):
            problem_classes.append(
                {
                    "class": "documentation_burden",
                    "instances": domain_context["instances"],
                    "frequency": "every_new_feature",
                }
            )

        return problem_classes

    def _design_framework(self, leverage_point: LeveragePoint) -> Dict:
        """Design framework at leverage point"""
        return {
            "name": f"{leverage_point.problem_domain}_framework",
            "type": "architectural_pattern",
            "leverage_point": leverage_point.description,
            "leverage_level": leverage_point.level.value,
            "impact": "Scales to all current + future instances",
        }

    async def _implement_frameworks(self, frameworks: List[Dict]) -> List[Dict]:
        """
        Implement designed frameworks

        **Extension Point**: Override to implement actual framework deployment
        (e.g., generating code templates, creating CI/CD pipelines, deploying
        infrastructure, setting up monitoring).

        This default implementation simulates framework deployment with validation
        and logging. Override for real framework deployment logic.

        Args:
            frameworks: List of framework dicts to implement

        Returns:
            List of result dicts with framework and deployed status
        """
        results = []
        for framework in frameworks:
            # Validate framework has required fields
            if not framework.get("name"):
                results.append({
                    "framework": framework,
                    "deployed": False,
                    "error": "Missing 'name' field"
                })
                continue

            # Log the framework deployment (in production, this would deploy real infrastructure)
            self.logger.info(f"Deploying systems framework: {framework.get('name')}", extra={
                "user_id": self.user_id,
                "framework_name": framework.get("name"),
                "framework_type": framework.get("type"),
                "leverage_level": framework.get("leverage_level")
            })

            # Simulate successful deployment
            results.append({
                "framework": framework,
                "deployed": True,
                "deployed_at": datetime.now().isoformat(),
                "status": "framework_active",
                "impact_scope": "system_wide"
            })

        return results

    # =========================================================================
    # FEEDBACK LOOP MANAGEMENT
    # =========================================================================

    def monitor_feedback_loops(self, session_history: List) -> Dict:
        """
        Detect and manage feedback loops in collaboration
        """
        active_loops = self.feedback_detector.detect_active_loop(session_history)

        # Take action based on loop type
        if active_loops.get("dominant_loop") == "R2_trust_erosion":
            # URGENT: Break vicious cycle
            return self._break_trust_erosion_loop()

        elif active_loops.get("dominant_loop") == "R1_trust_building":
            # MAINTAIN: Keep virtuous cycle going
            return self._maintain_trust_building_loop()

        return active_loops

    def _break_trust_erosion_loop(self) -> Dict:
        """Intervention to break vicious cycle of trust erosion"""
        return {
            "action": "transparency_intervention",
            "steps": [
                "Acknowledge misalignment explicitly",
                "Ask calibrated questions (Level 2)",
                "Reduce initiative temporarily (drop to Level 1-2)",
                "Rebuild trust through consistent small wins",
            ],
        }

    def _maintain_trust_building_loop(self) -> Dict:
        """Maintain virtuous cycle of trust building"""
        return {
            "action": "maintain_momentum",
            "steps": [
                "Continue current approach",
                "Gradually increase initiative (Level 3 → 4)",
                "Document successful patterns",
            ],
        }

    # =========================================================================
    # STATE MANAGEMENT
    # =========================================================================

    def get_collaboration_state(self) -> Dict:
        """Get current collaboration state"""
        return {
            "trust_level": self.collaboration_state.trust_level,
            "total_interactions": self.collaboration_state.total_interactions,
            "success_rate": (
                self.collaboration_state.successful_interventions
                / self.collaboration_state.total_interactions
                if self.collaboration_state.total_interactions > 0
                else 0
            ),
            "current_empathy_level": self.current_empathy_level,
            "target_empathy_level": self.target_level,
        }

    def reset_collaboration_state(self):
        """Reset collaboration state (new session)"""
        self.collaboration_state = CollaborationState()
