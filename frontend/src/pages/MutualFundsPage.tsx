import { HoldingsTransactionsTabs } from '../components/assets/HoldingsTransactionsTabs'
import { mutualFundsConfig, mutualFundTransactionsConfig } from '../assetConfigs'
import { useActiveProfile } from '../hooks/useActiveProfile'

export default function MutualFundsPage() {
  const { activeProfileId } = useActiveProfile()
  return (
    <HoldingsTransactionsTabs
      pageTitle="Mutual Funds"
      holdingsConfig={mutualFundsConfig}
      transactionsConfig={mutualFundTransactionsConfig}
      activeProfileId={activeProfileId}
    />
  )
}
