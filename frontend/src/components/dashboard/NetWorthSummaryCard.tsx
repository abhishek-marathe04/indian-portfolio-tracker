import { TrendingDown, TrendingUp } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { formatINR, formatPct } from '../../lib/formatters'
import { cn } from '../../lib/utils'

export function NetWorthSummaryCard({
  totalValue,
  gainLoss,
  gainLossPct,
}: {
  totalValue: number
  gainLoss: number
  gainLossPct: number
}) {
  const isGain = gainLoss >= 0

  return (
    <Card>
      <CardHeader>
        <CardTitle>Net Worth</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-3xl font-bold tracking-tight sm:text-4xl">{formatINR(totalValue)}</p>
        <div className={cn('mt-2 flex items-center gap-1.5 text-sm font-medium', isGain ? 'text-gain' : 'text-loss')}>
          {isGain ? <TrendingUp className="h-4 w-4" /> : <TrendingDown className="h-4 w-4" />}
          <span>
            {formatINR(Math.abs(gainLoss))} ({formatPct(Math.abs(gainLossPct))})
          </span>
        </div>
        <p className="mt-2 text-xs text-muted-foreground">
          Gain/Loss reflects Mutual Funds, Stocks, International Holdings &amp; Crypto only — FDs, Provident Fund,
          Gold, Real Estate and other categories contribute to Net Worth but don't carry an "invested amount" in
          this stat.
        </p>
      </CardContent>
    </Card>
  )
}
