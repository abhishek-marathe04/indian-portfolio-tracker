import { useEffect, useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { PageHeader } from '../components/common/PageHeader'
import { LoadingSpinner } from '../components/common/LoadingSpinner'
import { PortfolioValueChart } from '../components/performance/PortfolioValueChart'
import { XirrCard } from '../components/performance/XirrCard'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select'
import { useActiveProfile } from '../hooks/useActiveProfile'
import { fetchPerformance } from '../api/analytics'
import { makeAssetApi } from '../api/assets'
import type { XirrAssetType } from '../types/api'

const ASSET_TYPE_OPTIONS: { value: XirrAssetType; label: string }[] = [
  { value: 'all', label: 'All (Mutual Funds + Stocks)' },
  { value: 'mutual_funds', label: 'Mutual Funds' },
  { value: 'stocks', label: 'Stocks' },
]

const ALL_FOLIOS = 'all'

const mfHoldingsApi = makeAssetApi('mutual-funds')

export default function PerformancePage() {
  const { activeProfileId, activeProfile } = useActiveProfile()
  const [assetType, setAssetType] = useState<XirrAssetType>('all')
  const [folioNumber, setFolioNumber] = useState<string>(ALL_FOLIOS)

  const performanceQuery = useQuery({
    queryKey: ['performance', activeProfileId, assetType, folioNumber],
    queryFn: () => fetchPerformance(activeProfileId, assetType, folioNumber === ALL_FOLIOS ? null : folioNumber),
  })

  const mfHoldingsQuery = useQuery({
    queryKey: ['assets', 'mutual-funds', activeProfileId],
    queryFn: () => mfHoldingsApi.list(activeProfileId),
    enabled: assetType === 'mutual_funds',
  })

  const folioOptions = useMemo(() => {
    const byFolio = new Map<string, string>()
    for (const holding of mfHoldingsQuery.data ?? []) {
      const folio = String(holding.folio_number)
      if (!byFolio.has(folio)) byFolio.set(folio, String(holding.scheme_name ?? folio))
    }
    return Array.from(byFolio, ([value, schemeName]) => ({ value, label: `${schemeName} — Folio ${value}` }))
  }, [mfHoldingsQuery.data])

  function handleAssetTypeChange(v: XirrAssetType) {
    setAssetType(v)
    setFolioNumber(ALL_FOLIOS)
  }

  useEffect(() => {
    setFolioNumber(ALL_FOLIOS)
  }, [activeProfileId])

  const selectedFolioLabel =
    folioNumber !== ALL_FOLIOS ? folioOptions.find((opt) => opt.value === folioNumber)?.label : undefined

  return (
    <div>
      <PageHeader
        title="Performance"
        description={activeProfile ? `Showing ${activeProfile.name}'s portfolio` : 'Consolidated across all profiles'}
      />

      {performanceQuery.isLoading ? (
        <LoadingSpinner />
      ) : performanceQuery.isError || !performanceQuery.data ? (
        <p className="text-sm text-destructive">Failed to load performance data.</p>
      ) : (
        <div className="flex flex-col gap-6">
          <PortfolioValueChart data={performanceQuery.data.value_over_time} />

          <div className="flex flex-col gap-3">
            <div className="flex flex-col gap-3 sm:flex-row">
              <Select value={assetType} onValueChange={(v) => handleAssetTypeChange(v as XirrAssetType)}>
                <SelectTrigger className="w-full sm:w-64">
                  <SelectValue placeholder="Select asset type" />
                </SelectTrigger>
                <SelectContent>
                  {ASSET_TYPE_OPTIONS.map((opt) => (
                    <SelectItem key={opt.value} value={opt.value}>
                      {opt.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              {assetType === 'mutual_funds' && folioOptions.length > 0 && (
                <Select value={folioNumber} onValueChange={setFolioNumber}>
                  <SelectTrigger className="w-full sm:w-72">
                    <SelectValue placeholder="Select a folio" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value={ALL_FOLIOS}>All Mutual Funds</SelectItem>
                    {folioOptions.map((opt) => (
                      <SelectItem key={opt.value} value={opt.value}>
                        {opt.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              )}
            </div>

            <XirrCard
              xirrPct={performanceQuery.data.xirr_pct}
              note={performanceQuery.data.xirr_note}
              assetType={performanceQuery.data.xirr_asset_type}
              folioLabel={selectedFolioLabel}
            />
          </div>
        </div>
      )}
    </div>
  )
}
