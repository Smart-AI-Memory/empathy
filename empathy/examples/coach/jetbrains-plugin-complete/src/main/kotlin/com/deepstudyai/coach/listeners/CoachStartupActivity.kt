package com.deepstudyai.coach.listeners

import com.deepstudyai.coach.services.CoachProjectService
import com.intellij.openapi.project.Project
import com.intellij.openapi.startup.StartupActivity

/**
 * Startup activity that initializes Coach when a project is opened.
 */
class CoachStartupActivity : StartupActivity {

    override fun runActivity(project: Project) {
        // Initialize Coach for this project
        val projectService = CoachProjectService.getInstance(project)
        projectService.initialize()
    }
}
