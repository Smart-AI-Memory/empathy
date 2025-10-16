package com.deepstudyai.coach

import com.intellij.openapi.project.Project
import com.intellij.openapi.startup.StartupActivity

/**
 * Coach Plugin Entry Point
 * Initializes the plugin when project is opened
 *
 * Copyright 2025 Deep Study AI, LLC
 * Licensed under the Apache License, Version 2.0
 */
class CoachPlugin : StartupActivity {
    override fun runActivity(project: Project) {
        // Initialize LSP client
        val lspClient = project.getService(com.deepstudyai.coach.lsp.CoachLSPClient::class.java)
        lspClient.start()

        // Show welcome notification on first use
        val isFirstTime = PropertiesComponent.getInstance(project)
            .getBoolean("coach.firstActivation", true)

        if (isFirstTime) {
            showWelcomeNotification(project)
            PropertiesComponent.getInstance(project)
                .setValue("coach.firstActivation", false)
        }
    }

    private fun showWelcomeNotification(project: Project) {
        Notifications.Bus.notify(
            Notification(
                "Coach Notifications",
                "Coach AI Activated",
                "Welcome to Coach! AI with Level 4 Anticipatory Empathy.<br>" +
                "<a href=\"tutorial\">View Tutorial</a> | " +
                "<a href=\"wizards\">Browse Wizards</a>",
                NotificationType.INFORMATION
            ).setListener { notification, event ->
                when (event.description) {
                    "tutorial" -> BrowserUtil.browse("https://docs.coach-ai.dev/tutorial")
                    "wizards" -> {
                        val toolWindow = ToolWindowManager.getInstance(project)
                            .getToolWindow("Coach")
                        toolWindow?.show()
                    }
                }
            },
            project
        )
    }
}

// Required imports
import com.intellij.ide.util.PropertiesComponent
import com.intellij.notification.Notification
import com.intellij.notification.NotificationType
import com.intellij.notification.Notifications
import com.intellij.ide.BrowserUtil
import com.intellij.openapi.wm.ToolWindowManager
