import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Wizard } from '../../types/wizard'
import { ComplianceBadge } from '../common/ComplianceBadge'
import { ClassificationBadge } from '../common/ClassificationBadge'
import { EmpathyLevelIndicator } from '../common/EmpathyLevelIndicator'
import { WizardDemo } from '../WizardDemos'

interface WizardCardProps {
  wizard: Wizard
  isMobile?: boolean
}

export function WizardCard({ wizard, isMobile }: WizardCardProps) {
  const [isDemoExpanded, setIsDemoExpanded] = useState(false)

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className={`
        bg-white rounded-lg border-2 border-gray-200
        hover:border-primary-400 hover:shadow-lg
        transition-all duration-200
        ${isDemoExpanded ? 'md:col-span-2 lg:col-span-3' : ''}
      `}
    >
      {/* Card Header */}
      <div className="p-4 md:p-6">
        <div className="flex items-start gap-3">
          <span className="text-3xl md:text-4xl flex-shrink-0">{wizard.icon}</span>
          <div className="flex-1 min-w-0">
            <h3 className="text-lg md:text-xl font-bold text-gray-900 truncate">
              {wizard.name}
            </h3>
            <p className="text-sm text-gray-600 mt-1 line-clamp-2">
              {wizard.description}
            </p>
          </div>
        </div>

        {/* Badges */}
        <div className="flex flex-wrap gap-2 mt-4">
          {wizard.compliance.slice(0, isMobile ? 2 : 3).map((comp) => (
            <ComplianceBadge key={comp} compliance={comp} />
          ))}
          {wizard.compliance.length > (isMobile ? 2 : 3) && (
            <span className="text-xs text-gray-500 py-1">
              +{wizard.compliance.length - (isMobile ? 2 : 3)} more
            </span>
          )}
          <ClassificationBadge classification={wizard.classification} />
        </div>

        {/* Stats */}
        <div className="flex items-center gap-3 mt-4 text-sm text-gray-600">
          <EmpathyLevelIndicator level={wizard.empathyLevel} showLabel={false} />
          <span>·</span>
          <span>📊 {wizard.retentionDays}d</span>
          {!isMobile && (
            <>
              <span>·</span>
              <span>🔒 {wizard.piiPatterns.length} patterns</span>
            </>
          )}
        </div>

        {/* Actions */}
        <div className="flex gap-3 mt-4">
          <button
            onClick={() => setIsDemoExpanded(!isDemoExpanded)}
            className="
              w-full
              px-4 py-2 bg-primary-600 text-white rounded-lg
              font-medium hover:bg-primary-700 transition-colors
              flex items-center justify-center gap-2
            "
          >
            <span>{isDemoExpanded ? 'Hide Demo' : 'Try Demo'}</span>
            <motion.span
              animate={{ rotate: isDemoExpanded ? 180 : 0 }}
              transition={{ duration: 0.2 }}
            >
              ▼
            </motion.span>
          </button>
        </div>
      </div>

      {/* Inline Demo (Expandable) */}
      <AnimatePresence>
        {isDemoExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="border-t overflow-hidden"
          >
            <div className="p-4 md:p-6 bg-gray-50">
              <h4 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <span className="text-xl">{wizard.icon}</span>
                Interactive Demo: {wizard.name}
              </h4>
              <div className="bg-white rounded-lg border-2 border-gray-200 p-4 md:p-6">
                <WizardDemo wizardId={wizard.id} />
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}
