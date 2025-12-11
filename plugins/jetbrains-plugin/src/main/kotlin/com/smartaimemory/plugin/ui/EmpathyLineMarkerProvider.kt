package com.smartaimemory.plugin.ui

import com.intellij.codeInsight.daemon.LineMarkerInfo
import com.intellij.codeInsight.daemon.LineMarkerProvider
import com.intellij.psi.PsiElement

/**
 * Provides gutter icons for lines with Empathy Framework issues
 * (Stub implementation - will be fully implemented in Week 2)
 */
class EmpathyLineMarkerProvider : LineMarkerProvider {

    override fun getLineMarkerInfo(element: PsiElement): LineMarkerInfo<*>? {
        // TODO: Implement gutter icon display
        return null
    }
}
