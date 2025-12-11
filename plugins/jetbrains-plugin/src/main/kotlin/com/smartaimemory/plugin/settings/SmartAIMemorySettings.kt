package com.smartaimemory.plugin.settings

import com.intellij.openapi.components.*
import com.intellij.openapi.project.Project
import com.intellij.util.xmlb.XmlSerializerUtil

/**
 * Persistent settings for SmartAI Memory plugin
 */
@Service(Service.Level.PROJECT)
@State(
    name = "SmartAIMemorySettings",
    storages = [Storage("smartaimemory.xml")]
)
class SmartAIMemorySettings : PersistentStateComponent<SmartAIMemorySettings> {

    var empathyServiceUrl: String = "http://localhost:8000"
    var apiKey: String = ""
    var autoAnalyzeOnSave: Boolean = true
    var showInlineAnnotations: Boolean = true
    var memDocsRepoPath: String = ""
    var enablePredictions: Boolean = true
    var confidenceThreshold: Int = 70

    override fun getState(): SmartAIMemorySettings = this

    override fun loadState(state: SmartAIMemorySettings) {
        XmlSerializerUtil.copyBean(state, this)
    }

    companion object {
        fun getInstance(project: Project): SmartAIMemorySettings {
            return project.getService(SmartAIMemorySettings::class.java)
        }
    }
}
