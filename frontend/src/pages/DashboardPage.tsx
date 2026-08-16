import { useQuery } from '@tanstack/react-query'
import { PageHeader } from '../components/common/PageHeader'
import { LoadingSpinner } from '../components/common/LoadingSpinner'
import { NetWorthSummaryCard } from '../components/dashboard/NetWorthSummaryCard'
import { AllocationDonutChart } from '../components/dashboard/AllocationDonutChart'
import { useActiveProfile } from '../hooks/useActiveProfile'
import { fetchAllocation, fetchNetWorth } from '../api/analytics'
import { isConsolidatedNetWorth } from '../types/api'

export default function DashboardPage() {
  const { activeProfileId, activeProfile } = useActiveProfile()

  const netWorthQuery = useQuery({
    queryKey: ['net-worth', activeProfileId],
    queryFn: () => fetchNetWorth(activeProfileId),
  })

  const allocationQuery = useQuery({
    queryKey: ['allocation', activeProfileId],
    queryFn: () => fetchAllocation(activeProfileId),
  })

  const isLoading = netWorthQuery.isLoading || allocationQuery.isLoading

  const netWorthData = netWorthQuery.data
    ? isConsolidatedNetWorth(netWorthQuery.data)
      ? netWorthQuery.data.consolidated
      : netWorthQuery.data
    : null

  return (
    <div>
      <PageHeader
        title="Dashboard"
        description={activeProfile ? `Showing ${activeProfile.name}'s portfolio` : 'Consolidated across all profiles'}
      />

      {isLoading ? (
        <LoadingSpinner />
      ) : netWorthQuery.isError || !netWorthData ? (
        <p className="text-sm text-destructive">Failed to load net worth.</p>
      ) : (
        <div className="flex flex-col gap-6">
          <NetWorthSummaryCard
            totalValue={netWorthData.total_value}
            gainLoss={netWorthData.gain_loss}
            gainLossPct={netWorthData.gain_loss_pct}
          />

          {allocationQuery.data && (
            <AllocationDonutChart
              allocation={allocationQuery.data.allocation}
              breakdownInr={allocationQuery.data.breakdown_inr}
            />
          )}
        </div>
      )}
    </div>
  )
}
