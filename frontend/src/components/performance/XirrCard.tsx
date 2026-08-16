import { TrendingUp } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { formatPct } from '../../lib/formatters'
import { cn } from '../../lib/utils'
import type { XirrAssetType } from '../../types/api'

const TITLES: Record<XirrAssetType, string> = {
  all: 'XIRR',
  mutual_funds: 'Mutual Fund XIRR',
  stocks: 'Stock XIRR',
}

export function XirrCard({
  xirrPct,
  note,
  assetType,
  folioLabel,
}: {
  xirrPct: number | null
  note: string
  assetType: XirrAssetType
  folioLabel?: string
}) {
  const isGain = xirrPct !== null && xirrPct >= 0

  return (
    <Card>
      <CardHeader>
        <CardTitle>{folioLabel ?? TITLES[assetType]}</CardTitle>
      </CardHeader>
      <CardContent>
        {xirrPct === null ? (
          <p className="text-sm text-muted-foreground">
            Not enough transaction history yet to compute XIRR. Upload more CAS statements — the more of your
            purchase history is captured, the more accurate this becomes.
          </p>
        ) : (
          <>
            <div className={cn('flex items-center gap-1.5 text-3xl font-bold tracking-tight sm:text-4xl', isGain ? 'text-gain' : 'text-loss')}>
              <TrendingUp className="h-6 w-6" />
              <span>{formatPct(xirrPct)}</span>
            </div>
            <p className="mt-2 text-xs text-muted-foreground">{note}</p>
          </>
        )}
      </CardContent>
    </Card>
  )
}
