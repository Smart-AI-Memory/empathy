import { DataClassification } from '../../types/wizard'

interface ClassificationBadgeProps {
  classification: DataClassification
}

const classificationStyles: Record<
  DataClassification,
  { bg: string; text: string; icon: string }
> = {
  SENSITIVE: { bg: 'bg-red-100', text: 'text-red-700', icon: '🔴' },
  INTERNAL: { bg: 'bg-yellow-100', text: 'text-yellow-700', icon: '🟡' },
  PUBLIC: { bg: 'bg-green-100', text: 'text-green-700', icon: '🟢' },
}

export function ClassificationBadge({ classification }: ClassificationBadgeProps) {
  const style = classificationStyles[classification]

  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-1 rounded-md text-xs font-medium ${style.bg} ${style.text}`}
    >
      <span className="text-[10px]">{style.icon}</span>
      <span>{classification}</span>
    </span>
  )
}
