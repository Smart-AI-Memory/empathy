package com.smartaimemory.plugin.listeners

import com.intellij.openapi.project.Project
import com.intellij.openapi.vfs.newvfs.BulkFileListener
import com.intellij.openapi.vfs.newvfs.events.VFileEvent

/**
 * Listens for file saves and triggers auto-analysis
 * (Stub implementation - will be fully implemented in Week 3)
 */
class FileChangeListener(private val project: Project) : BulkFileListener {

    override fun after(events: List<VFileEvent>) {
        // TODO: Implement auto-analysis on save
    }
}
