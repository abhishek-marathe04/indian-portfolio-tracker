import { categoryColor, categoryLabel } from '../../lib/categories'
import { formatINR, formatPct } from '../../lib/formatters'

export function BreakdownList({
  allocation,
  breakdownInr,
}: {
  allocation: Record<string, number>
  breakdownInr: Record<string, number>
}) {
  const categories = Object.keys(allocation).sort((a, b) => (allocation[b] ?? 0) - (allocation[a] ?? 0))

  if (categories.length === 0) {
    return <p className="text-sm text-muted-foreground">No allocation data yet.</p>
  }

  return (
    <ul className="flex flex-col gap-2.5">
      {categories.map((key) => (
        <li key={key} className="flex items-center justify-between gap-3 text-sm">
          <span className="flex min-w-0 items-center gap-2">
            <span className="h-2.5 w-2.5 shrink-0 rounded-full" style={{ backgroundColor: categoryColor(key) }} />
            <span className="truncate">{categoryLabel(key)}</span>
          </span>
          <span className="flex shrink-0 items-center gap-2 tabular-nums">
            <span className="text-muted-foreground">{formatPct(allocation[key], 1)}</span>
            <span className="font-medium">{formatINR(breakdownInr[key] ?? 0)}</span>
          </span>
        </li>
      ))}
    </ul>
  )
}
