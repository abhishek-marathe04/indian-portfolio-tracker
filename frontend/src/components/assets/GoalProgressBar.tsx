import { formatINR } from '../../lib/formatters'
import { cn } from '../../lib/utils'

export function GoalProgressBar({ current, target }: { current: number; target: number }) {
  const pct = target > 0 ? Math.min(100, Math.round((current / target) * 100)) : 0

  return (
    <div className="flex min-w-[180px] flex-col gap-1">
      <div className="flex items-center justify-between text-xs">
        <span className="font-medium">{formatINR(current)}</span>
        <span className="text-muted-foreground">{pct}%</span>
      </div>
      <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
        <div
          className={cn('h-full rounded-full transition-all', pct >= 100 ? 'bg-gain' : 'bg-primary')}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="text-[11px] text-muted-foreground">of {formatINR(target)}</span>
    </div>
  )
}
