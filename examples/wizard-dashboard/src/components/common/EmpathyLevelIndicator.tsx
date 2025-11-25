interface EmpathyLevelIndicatorProps {
  level: 3 | 4 | 5
  showLabel?: boolean
}

const levelConfig = {
  3: {
    label: 'Proactive',
    color: 'text-orange-600',
    bars: 3,
    icon: '❤️',
  },
  4: {
    label: 'Anticipatory',
    color: 'text-red-600',
    bars: 4,
    icon: '❤️',
  },
  5: {
    label: 'Transformative',
    color: 'text-purple-600',
    bars: 5,
    icon: '❤️',
  },
}

export function EmpathyLevelIndicator({
  level,
  showLabel = true,
}: EmpathyLevelIndicatorProps) {
  const config = levelConfig[level]

  return (
    <div className="inline-flex items-center gap-2">
      <span className={config.color}>{config.icon}</span>
      {showLabel && (
        <span className="text-sm">
          <span className="font-medium">Level {level}:</span>{' '}
          <span className="text-gray-600">{config.label}</span>
        </span>
      )}
      {!showLabel && (
        <div className="flex gap-0.5">
          {[...Array(5)].map((_, i) => (
            <div
              key={i}
              className={`w-1 h-3 rounded-sm ${
                i < config.bars ? config.color.replace('text-', 'bg-') : 'bg-gray-200'
              }`}
            />
          ))}
        </div>
      )}
    </div>
  )
}
