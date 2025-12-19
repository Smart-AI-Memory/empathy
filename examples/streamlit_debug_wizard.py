"""
Streamlit Prototype - Memory-Enhanced Debugging Wizard

Interactive web interface for the Memory-Enhanced Debugging Wizard,
demonstrating Level 4+ Anticipatory Empathy with persistent memory.

Features:
- File upload for code analysis (Web Demo: 5 file limit)
- Local folder path input for production use
- Error message and stack trace analysis
- Historical bug pattern correlation
- Fix recommendations based on team knowledge

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import asyncio
import sys
from pathlib import Path

# Ensure the parent directory is in path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import streamlit as st
except ImportError:
    print("Error: Streamlit is not installed.")
    print("Please install it with: pip install streamlit")
    print("Or use: pip install -r examples/requirements-streamlit.txt")
    sys.exit(1)

# Try to import the wizard - graceful fallback if dependencies missing
WIZARD_AVAILABLE = False
IMPORT_ERROR = None

try:
    from empathy_software_plugin.wizards import MemoryEnhancedDebuggingWizard

    WIZARD_AVAILABLE = True
except ImportError as e:
    IMPORT_ERROR = str(e)
except Exception as e:
    IMPORT_ERROR = f"Unexpected error: {e}"


# Page configuration
st.set_page_config(
    page_title="Memory-Enhanced Debugging Wizard",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)


def init_session_state():
    """Initialize session state variables."""
    if "analysis_results" not in st.session_state:
        st.session_state.analysis_results = None
    if "analysis_history" not in st.session_state:
        st.session_state.analysis_history = []
    if "wizard" not in st.session_state:
        st.session_state.wizard = None


def create_wizard(pattern_path: str = "./patterns/debugging"):
    """Create or get existing wizard instance."""
    if st.session_state.wizard is None and WIZARD_AVAILABLE:
        st.session_state.wizard = MemoryEnhancedDebuggingWizard(pattern_storage_path=pattern_path)
    return st.session_state.wizard


def render_sidebar():
    """Render the sidebar with configuration options."""
    with st.sidebar:
        st.title("Configuration")
        st.markdown("---")

        # Deployment mode toggle
        deployment_mode = st.radio(
            "Deployment Mode",
            options=["Web Demo", "Local"],
            index=0,
            help="Web Demo has file limits. Local mode allows folder paths.",
        )

        st.markdown("---")

        # Mode-specific information
        if deployment_mode == "Web Demo":
            st.info(
                "**Web Demo Mode**\n\n"
                "- Maximum 5 files\n"
                "- 1MB per file limit\n"
                "- Pattern storage in memory only"
            )
            st.markdown("---")
            st.markdown("### Upgrade to Full Version")
            st.markdown(
                "Get unlimited file analysis, persistent pattern storage, "
                "and team collaboration features."
            )
            if st.button("Learn More", type="primary"):
                st.markdown("[Visit Empathy Framework](https://github.com/empathy-framework)")
        else:
            st.success(
                "**Local Mode**\n\n"
                "- Unlimited files\n"
                "- Folder path support\n"
                "- Persistent pattern storage"
            )

            # Pattern storage path
            pattern_path = st.text_input(
                "Pattern Storage Path",
                value="./patterns/debugging",
                help="Directory for storing bug patterns",
            )

        st.markdown("---")

        # About section
        st.markdown("### About")
        st.markdown(
            "**Memory-Enhanced Debugging Wizard**\n\n"
            "Level 4+ Anticipatory Empathy\n\n"
            "Correlates current bugs with historical patterns "
            "to recommend proven fixes."
        )

        st.markdown("---")
        st.markdown("*Empathy Framework v2.2.7*\n\nCopyright 2025 Smart AI Memory, LLC")

        return deployment_mode, (
            pattern_path if deployment_mode == "Local" else "./patterns/debugging"
        )


def render_file_upload(deployment_mode: str):
    """Render file upload section."""
    st.markdown("### Code Files")

    if deployment_mode == "Web Demo":
        st.caption("Upload up to 5 files (max 1MB each)")
        uploaded_files = st.file_uploader(
            "Upload code files for analysis",
            accept_multiple_files=True,
            type=["py", "js", "ts", "tsx", "jsx", "java", "go", "rs", "cpp", "c", "h"],
            key="file_uploader",
        )

        if uploaded_files and len(uploaded_files) > 5:
            st.warning("Web Demo is limited to 5 files. Only the first 5 will be analyzed.")
            uploaded_files = uploaded_files[:5]

        return uploaded_files
    else:
        return None


def render_folder_input(deployment_mode: str):
    """Render folder path input for local mode."""
    if deployment_mode == "Local":
        st.markdown("### Project Path")
        folder_path = st.text_input(
            "Enter folder path to analyze",
            placeholder="/path/to/your/project",
            help="Full path to your project directory",
        )

        if folder_path:
            path = Path(folder_path)
            if path.exists() and path.is_dir():
                st.success(f"Found {len(list(path.rglob('*.py')))} Python files")
            elif folder_path:
                st.error("Directory not found")

        return folder_path
    return None


def render_error_input():
    """Render error message and stack trace inputs."""
    st.markdown("### Error Details")

    col1, col2 = st.columns(2)

    with col1:
        error_message = st.text_input(
            "Error Message",
            placeholder="e.g., TypeError: Cannot read property 'map' of undefined",
            help="The main error message you're seeing",
        )

        file_path = st.text_input(
            "File Path (optional)",
            placeholder="e.g., src/components/UserList.tsx",
            help="The file where the error occurred",
        )

    with col2:
        line_number = st.number_input(
            "Line Number (optional)", min_value=0, value=0, help="Line number of the error"
        )

        correlate_history = st.checkbox(
            "Correlate with historical bugs",
            value=True,
            help="Search pattern storage for similar past bugs",
        )

    stack_trace = st.text_area(
        "Stack Trace (optional)",
        placeholder="Paste the full stack trace here...",
        height=150,
        help="The complete error stack trace",
    )

    code_snippet = st.text_area(
        "Code Snippet (optional)",
        placeholder="Paste the relevant code snippet here...",
        height=100,
        help="The code surrounding the error",
    )

    return {
        "error_message": error_message,
        "file_path": file_path or "unknown",
        "line_number": line_number if line_number > 0 else None,
        "stack_trace": stack_trace,
        "code_snippet": code_snippet,
        "correlate_with_history": correlate_history,
    }


def render_results(results: dict):
    """Render analysis results."""
    if not results:
        return

    st.markdown("---")
    st.markdown("## Analysis Results")

    # Error Classification
    with st.expander("Error Classification", expanded=True):
        classification = results.get("error_classification", {})

        col1, col2, col3 = st.columns(3)

        with col1:
            error_type = classification.get("error_type", "unknown")
            st.metric("Error Type", error_type.replace("_", " ").title())

        with col2:
            confidence = results.get("confidence", 0)
            st.metric("Confidence", f"{confidence:.0%}")

        with col3:
            matches_found = results.get("matches_found", 0)
            st.metric("Historical Matches", matches_found)

        # Likely causes
        likely_causes = classification.get("likely_causes", [])
        if likely_causes:
            st.markdown("**Likely Causes:**")
            for cause in likely_causes:
                likelihood = cause.get("likelihood", 0)
                cause_text = cause.get("cause", "Unknown")
                check_text = cause.get("check", "")
                st.markdown(
                    f"- **{cause_text}** ({likelihood:.0%} likelihood)\n  - Check: {check_text}"
                )

    # Historical Matches
    historical_matches = results.get("historical_matches", [])
    if historical_matches:
        with st.expander("Historical Matches", expanded=True):
            st.markdown("Similar bugs from the past:")

            for i, match in enumerate(historical_matches, 1):
                with st.container():
                    st.markdown(f"### Match #{i}")

                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown(f"**Date:** {match.get('date', 'Unknown')}")
                        st.markdown(f"**File:** `{match.get('file', 'Unknown')}`")
                        st.markdown(f"**Error Type:** {match.get('error_type', 'Unknown')}")

                    with col2:
                        similarity = match.get("similarity_score", 0)
                        st.markdown(f"**Similarity:** {similarity:.0%}")
                        res_time = match.get("resolution_time_minutes", 0)
                        st.markdown(f"**Resolution Time:** {res_time} min")

                    st.markdown(f"**Root Cause:** {match.get('root_cause', 'Not recorded')}")
                    st.markdown(f"**Fix Applied:** {match.get('fix_applied', 'Not recorded')}")

                    fix_code = match.get("fix_code")
                    if fix_code:
                        st.markdown("**Fix Code:**")
                        st.code(fix_code)

                    matching_factors = match.get("matching_factors", [])
                    if matching_factors:
                        st.markdown("**Matching Factors:**")
                        for factor in matching_factors:
                            st.markdown(f"- {factor}")

                    st.markdown("---")

    # Recommended Fix
    recommended_fix = results.get("recommended_fix")
    if recommended_fix:
        with st.expander("Recommended Fix", expanded=True):
            st.success(f"Based on: {recommended_fix.get('based_on', 'Historical patterns')}")

            st.markdown(f"**Original Fix:** {recommended_fix.get('original_fix', 'N/A')}")
            st.markdown(
                f"**Expected Resolution Time:** {recommended_fix.get('expected_resolution_time', 'N/A')}"
            )
            st.markdown(f"**Confidence:** {recommended_fix.get('confidence', 0):.0%}")

            fix_code = recommended_fix.get("fix_code")
            if fix_code:
                st.markdown("**Fix Code:**")
                st.code(fix_code)

            adaptation_notes = recommended_fix.get("adaptation_notes", [])
            if adaptation_notes:
                st.markdown("**Adaptation Notes:**")
                for note in adaptation_notes:
                    st.markdown(f"- {note}")

    # Time Saved Estimate
    memory_benefit = results.get("memory_benefit", {})
    if memory_benefit:
        with st.expander("Time Saved", expanded=True):
            col1, col2 = st.columns(2)

            with col1:
                time_saved = memory_benefit.get("time_saved_estimate", "N/A")
                st.metric("Estimated Time Saved", time_saved)

            with col2:
                matches = memory_benefit.get("matches_found", 0)
                st.metric("Patterns Matched", matches)

            st.info(memory_benefit.get("value_statement", ""))

            historical_insight = memory_benefit.get("historical_insight")
            if historical_insight:
                st.markdown(f"**Key Insight:** {historical_insight}")

    # Predictions
    predictions = results.get("predictions", [])
    if predictions:
        with st.expander("Predictions (Level 4)", expanded=True):
            for pred in predictions:
                severity = pred.get("severity", "info")
                severity_icons = {
                    "high": "warning",
                    "medium": "info",
                    "info": "success",
                    "low": "success",
                }

                icon = severity_icons.get(severity, "info")

                if icon == "warning":
                    st.warning(pred.get("description", ""))
                elif icon == "info":
                    st.info(pred.get("description", ""))
                else:
                    st.success(pred.get("description", ""))

                prevention_steps = pred.get("prevention_steps", [])
                if prevention_steps:
                    st.markdown("**Prevention Steps:**")
                    for step in prevention_steps:
                        st.markdown(f"- {step}")

    # Recommendations
    recommendations = results.get("recommendations", [])
    if recommendations:
        with st.expander("Recommendations", expanded=True):
            for rec in recommendations:
                st.markdown(f"- {rec}")


def render_demo_mode_fallback():
    """Render a demo mode when wizard is not available."""
    st.warning(
        "The Memory-Enhanced Debugging Wizard could not be imported. "
        "Running in demo mode with simulated results.\n\n"
        f"Import error: {IMPORT_ERROR}"
    )

    return {
        "error_classification": {
            "error_type": "null_reference",
            "error_message": "Demo error message",
            "file_path": "demo/file.py",
            "line_number": 42,
            "file_type": ".py",
            "likely_causes": [
                {
                    "cause": "Accessing property before data loads",
                    "check": "Add null/undefined check before access",
                    "likelihood": 0.7,
                },
                {
                    "cause": "API returned null unexpectedly",
                    "check": "Verify API response structure",
                    "likelihood": 0.5,
                },
            ],
        },
        "historical_matches": [
            {
                "date": "2025-11-15",
                "file": "src/api/users.py",
                "error_type": "null_reference",
                "root_cause": "API returned null instead of empty array",
                "fix_applied": "Added default empty array fallback",
                "fix_code": "data = response.get('items', [])",
                "resolution_time_minutes": 15,
                "similarity_score": 0.85,
                "matching_factors": [
                    "Same error type: null_reference",
                    "Same file type: .py",
                    "Similar error message (72% match)",
                ],
            }
        ],
        "matches_found": 1,
        "recommended_fix": {
            "based_on": "Bug #demo_001 from 2025-11-15",
            "original_fix": "Added default empty array fallback",
            "fix_code": "data = response.get('items', [])",
            "expected_resolution_time": "15 minutes",
            "confidence": 0.85,
            "adaptation_notes": ["Adapt the fix pattern for your specific data structure"],
        },
        "predictions": [
            {
                "type": "related_null_errors",
                "severity": "medium",
                "description": (
                    "Based on patterns, null reference errors often cluster. "
                    "Check similar components for the same issue."
                ),
                "prevention_steps": [
                    "Add defensive null checks across related files",
                    "Consider TypeScript strict null checks",
                    "Review API contract for nullable fields",
                ],
            }
        ],
        "recommendations": [
            "Historical match found! Try: Added default empty array fallback",
            "Example fix code available from Bug #demo_001",
            "Check: Accessing property before data loads - Add null/undefined check",
            "Memory saved you time: 1 similar bug found instantly",
        ],
        "confidence": 0.85,
        "memory_benefit": {
            "matches_found": 1,
            "time_saved_estimate": "~9 minutes",
            "value_statement": (
                "Persistent memory found 1 similar bug. "
                "Without memory, you'd start from zero every time."
            ),
            "historical_insight": "Added default empty array fallback",
        },
    }


async def run_analysis(wizard, context: dict) -> dict:
    """Run the wizard analysis asynchronously."""
    return await wizard.analyze(context)


def main():
    """Main application entry point."""
    init_session_state()

    # Header
    st.title("Memory-Enhanced Debugging Wizard")
    st.markdown("Level 4+ Anticipatory Empathy - Correlate bugs with historical patterns")

    # Sidebar
    deployment_mode, pattern_path = render_sidebar()

    # Main content
    col1, col2 = st.columns([2, 1])

    with col1:
        # File upload (Web Demo mode)
        uploaded_files = render_file_upload(deployment_mode)

        # Folder input (Local mode)
        _folder_path = render_folder_input(deployment_mode)  # noqa: F841

    with col2:
        # Display uploaded files
        if uploaded_files:
            st.markdown("### Uploaded Files")
            for f in uploaded_files:
                st.markdown(f"- `{f.name}` ({f.size / 1024:.1f} KB)")

    st.markdown("---")

    # Error input
    error_context = render_error_input()

    # Analyze button
    st.markdown("---")

    col1, col2, col3 = st.columns([1, 1, 1])

    with col2:
        analyze_button = st.button(
            "Analyze Bug",
            type="primary",
            use_container_width=True,
            disabled=not error_context.get("error_message"),
        )

    # Run analysis
    if analyze_button and error_context.get("error_message"):
        with st.spinner("Analyzing bug and searching historical patterns..."):
            if WIZARD_AVAILABLE:
                wizard = create_wizard(pattern_path)
                try:
                    # Run async analysis
                    results = asyncio.run(run_analysis(wizard, error_context))
                    st.session_state.analysis_results = results
                    st.session_state.analysis_history.append(
                        {"context": error_context, "results": results}
                    )
                except Exception as e:
                    st.error(f"Analysis failed: {e}")
                    st.session_state.analysis_results = None
            else:
                # Demo mode fallback
                st.session_state.analysis_results = render_demo_mode_fallback()

    # Display results
    if st.session_state.analysis_results:
        render_results(st.session_state.analysis_results)

    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray;'>"
        "Empathy Framework v2.2.7 | "
        "Memory-Enhanced Debugging Wizard | "
        "Level 4+ Anticipatory Empathy"
        "</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
