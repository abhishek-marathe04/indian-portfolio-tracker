import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { formatINR } from '../../lib/formatters'
import type { PortfolioValuePoint } from '../../types/api'

function monthLabel(month: string): string {
  const d = new Date(`${month}T00:00:00`)
  if (Number.isNaN(d.getTime())) return month
  return d.toLocaleDateString('en-IN', { month: 'short', year: '2-digit' })
}

interface TooltipPayloadItem {
  value: number
  payload: PortfolioValuePoint
}

function ChartTooltip({ active, payload }: { active?: boolean; payload?: TooltipPayloadItem[] }) {
  if (!active || !payload || payload.length === 0) return null
  const point = payload[0].payload
  return (
    <div className="rounded-md border border-border bg-popover px-3 py-2 text-sm text-popover-foreground shadow-md">
      <p className="font-medium">{monthLabel(point.month)}</p>
      <p className="text-muted-foreground">{formatINR(point.total_value)}</p>
    </div>
  )
}

export function PortfolioValueChart({ data }: { data: PortfolioValuePoint[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Portfolio Value Over Time</CardTitle>
      </CardHeader>
      <CardContent>
        {data.length === 0 ? (
          <p className="text-sm text-muted-foreground">
            No history yet. Upload CAS statements spread across past months/years — each one contributes its own
            trailing 12-month valuation trend, and overlapping uploads build up a continuous history.
          </p>
        ) : (
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data} margin={{ top: 8, right: 16, bottom: 0, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" vertical={false} />
                <XAxis
                  dataKey="month"
                  tickFormatter={monthLabel}
                  tick={{ fontSize: 12, fill: 'hsl(var(--muted-foreground))' }}
                  axisLine={{ stroke: 'hsl(var(--border))' }}
                  tickLine={false}
                />
                <YAxis
                  tickFormatter={(v: number) => formatINR(v)}
                  tick={{ fontSize: 12, fill: 'hsl(var(--muted-foreground))' }}
                  axisLine={false}
                  tickLine={false}
                  width={90}
                />
                <Tooltip content={<ChartTooltip />} />
                <Line
                  type="monotone"
                  dataKey="total_value"
                  stroke="hsl(var(--primary))"
                  strokeWidth={2}
                  dot={{ r: 3, fill: 'hsl(var(--primary))' }}
                  activeDot={{ r: 5 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
