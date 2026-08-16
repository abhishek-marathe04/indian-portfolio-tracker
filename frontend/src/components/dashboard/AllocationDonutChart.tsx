import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { BreakdownList } from './BreakdownList'
import { categoryColor, categoryLabel } from '../../lib/categories'
import { formatPct } from '../../lib/formatters'

interface TooltipPayloadItem {
  name: string
  value: number
}

function ChartTooltip({ active, payload }: { active?: boolean; payload?: TooltipPayloadItem[] }) {
  if (!active || !payload || payload.length === 0) return null
  const item = payload[0]
  return (
    <div className="rounded-md border border-border bg-popover px-3 py-2 text-sm text-popover-foreground shadow-md">
      <p className="font-medium">{categoryLabel(item.name)}</p>
      <p className="text-muted-foreground">{formatPct(item.value, 1)}</p>
    </div>
  )
}

export function AllocationDonutChart({
  allocation,
  breakdownInr,
}: {
  allocation: Record<string, number>
  breakdownInr?: Record<string, number>
}) {
  const data = Object.entries(allocation)
    .map(([key, pct]) => ({ name: key, value: pct }))
    .sort((a, b) => b.value - a.value)

  return (
    <Card>
      <CardHeader>
        <CardTitle>Allocation</CardTitle>
      </CardHeader>
      <CardContent>
        {data.length === 0 ? (
          <p className="text-sm text-muted-foreground">No allocation data yet.</p>
        ) : (
          <div className="flex flex-col gap-6 md:flex-row md:items-center">
            <div className="mx-auto h-64 w-64 shrink-0">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={data} dataKey="value" nameKey="name" innerRadius="60%" outerRadius="90%" paddingAngle={1}>
                    {data.map((entry) => (
                      <Cell key={entry.name} fill={categoryColor(entry.name)} stroke="hsl(var(--card))" strokeWidth={2} />
                    ))}
                  </Pie>
                  <Tooltip content={<ChartTooltip />} />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="min-w-0 flex-1">
              <BreakdownList allocation={allocation} breakdownInr={breakdownInr ?? {}} />
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
