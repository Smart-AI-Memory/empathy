package com.deepstudyai.coach.templates

import com.intellij.ide.util.projectWizard.WizardContext
import com.intellij.platform.ProjectTemplate
import com.intellij.platform.ProjectTemplatesFactory
import javax.swing.Icon
import com.intellij.openapi.util.IconLoader

/**
 * Factory for Coach wizard project templates.
 *
 * This is a key Approach 2 feature that allows users to create new
 * Coach wizard projects from templates.
 */
class CoachProjectTemplateFactory : ProjectTemplatesFactory() {

    companion object {
        private val COACH_ICON: Icon = IconLoader.getIcon("/icons/coach.svg", CoachProjectTemplateFactory::class.java)
    }

    override fun getGroupName(): String = "Coach"

    override fun getGroupIcon(): Icon = COACH_ICON

    override fun createTemplates(group: String?, context: WizardContext): Array<ProjectTemplate> {
        return arrayOf(
            CoachWizardProjectTemplate(),
            CoachMultiWizardProjectTemplate()
        )
    }
}

/**
 * Template for creating a basic Coach wizard project.
 */
class CoachWizardProjectTemplate : ProjectTemplate {

    override fun getName(): String = "Coach Wizard Project"

    override fun getDescription(): String =
        "Create a new project for developing custom Coach wizards"

    override fun getIcon(): Icon =
        IconLoader.getIcon("/icons/new-wizard.svg", CoachWizardProjectTemplate::class.java)

    override fun createModuleBuilder(): com.intellij.ide.util.projectWizard.ModuleBuilder {
        return CoachWizardModuleBuilder()
    }

    override fun validateSettings(): com.intellij.openapi.ui.ValidationInfo? = null
}

/**
 * Template for creating a multi-wizard collaboration project.
 */
class CoachMultiWizardProjectTemplate : ProjectTemplate {

    override fun getName(): String = "Coach Multi-Wizard Project"

    override fun getDescription(): String =
        "Create a project with multiple collaborative Coach wizards"

    override fun getIcon(): Icon =
        IconLoader.getIcon("/icons/collaboration.svg", CoachMultiWizardProjectTemplate::class.java)

    override fun createModuleBuilder(): com.intellij.ide.util.projectWizard.ModuleBuilder {
        return CoachWizardModuleBuilder(multiWizard = true)
    }

    override fun validateSettings(): com.intellij.openapi.ui.ValidationInfo? = null
}
