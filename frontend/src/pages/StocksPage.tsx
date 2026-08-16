import { HoldingsTransactionsTabs } from '../components/assets/HoldingsTransactionsTabs'
import { stocksConfig, stockTransactionsConfig } from '../assetConfigs'
import { useActiveProfile } from '../hooks/useActiveProfile'

export default function StocksPage() {
  const { activeProfileId } = useActiveProfile()
  return (
    <HoldingsTransactionsTabs
      pageTitle="Stocks"
      holdingsConfig={stocksConfig}
      transactionsConfig={stockTransactionsConfig}
      activeProfileId={activeProfileId}
    />
  )
}
