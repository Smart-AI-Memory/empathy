package com.deepstudyai.coach.templates

import com.intellij.ide.util.projectWizard.ModuleBuilder
import com.intellij.ide.util.projectWizard.ModuleWizardStep
import com.intellij.ide.util.projectWizard.WizardContext
import com.intellij.openapi.module.ModuleType
import com.intellij.openapi.roots.ModifiableRootModel
import com.intellij.openapi.vfs.VirtualFile
import java.io.File

/**
 * Module builder for Coach wizard projects.
 *
 * Creates the project structure and initial files for custom wizard development.
 */
class CoachWizardModuleBuilder(private val multiWizard: Boolean = false) : ModuleBuilder() {

    override fun getModuleType(): ModuleType<*> = ModuleType.EMPTY

    override fun setupRootModel(modifiableRootModel: ModifiableRootModel) {
        val contentEntry = doAddContentEntry(modifiableRootModel) ?: return
        val root = contentEntry.file ?: return

        // Create project structure
        createProjectStructure(root)
    }

    private fun createProjectStructure(root: VirtualFile) {
        val rootPath = root.path

        // Create directory structure
        File("$rootPath/wizards").mkdir()
        File("$rootPath/tests").mkdir()
        File("$rootPath/config").mkdir()

        // Create README
        File("$rootPath/README.md").writeText(
            """
            # Coach Wizard Project

            This project contains custom Coach wizards.

            ## Structure

            - `wizards/` - Custom wizard implementations
            - `tests/` - Unit tests for wizards
            - `config/` - Configuration files

            ## Getting Started

            1. Create a new wizard in the `wizards/` directory
            2. Implement the wizard using the Coach framework
            3. Test your wizard in the `tests/` directory
            4. Configure wizard settings in `config/wizard_config.yaml`

            ## Example Wizard

            See `wizards/example_wizard.py` for a template.
            """.trimIndent()
        )

        // Create example wizard
        File("$rootPath/wizards/example_wizard.py").writeText(
            """
            from coach.base_wizard import BaseWizard
            from coach.types import WizardResult, Severity

            class ExampleWizard(BaseWizard):
                """
                Example custom wizard.

                This wizard demonstrates how to create a custom Coach wizard.
                """

                def __init__(self):
                    super().__init__(
                        name="ExampleWizard",
                        description="An example custom wizard",
                        version="1.0.0"
                    )

                def analyze(self, code: str, context: dict) -> WizardResult:
                    """
                    Analyze the code and return results.

                    Args:
                        code: The source code to analyze
                        context: Additional context (role, task, etc.)

                    Returns:
                        WizardResult with diagnosis and recommendations
                    """
                    # TODO: Implement your analysis logic here

                    return WizardResult(
                        wizard=self.name,
                        diagnosis="Example analysis complete",
                        severity=Severity.INFO,
                        recommendations=[
                            "This is an example recommendation"
                        ],
                        code_examples=[],
                        references=[]
                    )
            """.trimIndent()
        )

        // Create wizard config
        File("$rootPath/config/wizard_config.yaml").writeText(
            """
            # Coach Wizard Configuration

            wizards:
              - name: ExampleWizard
                enabled: true
                module: wizards.example_wizard
                class: ExampleWizard
                settings:
                  # Add wizard-specific settings here
                  severity_threshold: WARNING

            # Global settings
            settings:
              cache_enabled: true
              timeout_seconds: 60
            """.trimIndent()
        )

        // Create test file
        File("$rootPath/tests/test_example_wizard.py").writeText(
            """
            import pytest
            from wizards.example_wizard import ExampleWizard

            def test_example_wizard_basic():
                """Test basic functionality of ExampleWizard."""
                wizard = ExampleWizard()

                code = '''
                def hello():
                    print("Hello, World!")
                '''

                result = wizard.analyze(code, {})

                assert result.wizard == "ExampleWizard"
                assert result.diagnosis is not None
                assert len(result.recommendations) > 0

            def test_example_wizard_with_context():
                """Test ExampleWizard with context."""
                wizard = ExampleWizard()

                code = "# Some code"
                context = {
                    "role": "developer",
                    "task": "Review code quality"
                }

                result = wizard.analyze(code, context)
                assert result is not None
            """.trimIndent()
        )

        if (multiWizard) {
            // Create additional wizards for multi-wizard project
            File("$rootPath/wizards/quality_wizard.py").writeText(
                """
                from coach.base_wizard import BaseWizard
                from coach.types import WizardResult, Severity

                class QualityWizard(BaseWizard):
                    """Checks code quality metrics."""

                    def __init__(self):
                        super().__init__(
                            name="QualityWizard",
                            description="Code quality analysis",
                            version="1.0.0"
                        )

                    def analyze(self, code: str, context: dict) -> WizardResult:
                        # TODO: Implement quality analysis
                        return WizardResult(
                            wizard=self.name,
                            diagnosis="Quality analysis pending",
                            severity=Severity.INFO,
                            recommendations=[],
                            code_examples=[],
                            references=[]
                        )
                """.trimIndent()
            )

            // Create collaboration config
            File("$rootPath/config/collaboration.yaml").writeText(
                """
                # Multi-Wizard Collaboration Configuration

                scenarios:
                  - name: code_review
                    wizards:
                      - ExampleWizard
                      - QualityWizard
                    description: Comprehensive code review

                  - name: security_audit
                    wizards:
                      - ExampleWizard
                    description: Security-focused review
                """.trimIndent()
            )
        }

        // Create requirements.txt
        File("$rootPath/requirements.txt").writeText(
            """
            coach-framework>=0.1.0
            langchain>=0.1.0
            pytest>=7.0.0
            pyyaml>=6.0
            """.trimIndent()
        )

        // Refresh the file system
        root.refresh(false, true)
    }

    override fun getCustomOptionsStep(context: WizardContext, parentDisposable: com.intellij.openapi.Disposable): ModuleWizardStep? {
        return null // No custom options for now
    }
}
