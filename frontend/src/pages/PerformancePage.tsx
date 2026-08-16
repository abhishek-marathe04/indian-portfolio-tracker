import { useQuery } from '@tanstack/react-query'
import { PageHeader } from '../components/common/PageHeader'
import { LoadingSpinner } from '../components/common/LoadingSpinner'
import { PortfolioValueChart } from '../components/performance/PortfolioValueChart'
import { MfXirrCard } from '../components/performance/MfXirrCard'
import { useActiveProfile } from '../hooks/useActiveProfile'
import { fetchPerformance } from '../api/analytics'

export default function PerformancePage() {
  const { activeProfileId, activeProfile } = useActiveProfile()

  const performanceQuery = useQuery({
    queryKey: ['performance', activeProfileId],
    queryFn: () => fetchPerformance(activeProfileId),
  })

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
          <MfXirrCard xirrPct={performanceQuery.data.mf_xirr_pct} note={performanceQuery.data.mf_xirr_note} />
        </div>
      )}
    </div>
  )
}
