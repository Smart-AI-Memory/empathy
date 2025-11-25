interface ComplianceBadgeProps {
  compliance: string
}

const badgeStyles: Record<string, { bg: string; text: string; icon: string }> = {
  HIPAA: { bg: 'bg-blue-100', text: 'text-blue-700', icon: '🏥' },
  SOX: { bg: 'bg-green-100', text: 'text-green-700', icon: '💼' },
  'PCI-DSS': { bg: 'bg-orange-100', text: 'text-orange-700', icon: '💳' },
  FERPA: { bg: 'bg-purple-100', text: 'text-purple-700', icon: '🎓' },
  GDPR: { bg: 'bg-blue-100', text: 'text-blue-700', icon: '🌍' },
  FISMA: { bg: 'bg-red-100', text: 'text-red-700', icon: '🏛️' },
  IRB: { bg: 'bg-teal-100', text: 'text-teal-700', icon: '🔬' },
  SOC2: { bg: 'bg-indigo-100', text: 'text-indigo-700', icon: '🛡️' },
  'ISO 27001': { bg: 'bg-gray-100', text: 'text-gray-700', icon: '📋' },
}

export function ComplianceBadge({ compliance }: ComplianceBadgeProps) {
  const style = badgeStyles[compliance] || {
    bg: 'bg-gray-100',
    text: 'text-gray-700',
    icon: '📋',
  }

  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-1 rounded-md text-xs font-medium ${style.bg} ${style.text}`}
    >
      <span>{style.icon}</span>
      <span>{compliance}</span>
    </span>
  )
}
