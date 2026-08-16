import { AssetCrudPage } from '../components/assets/AssetCrudPage'
import { savingsAccountsConfig } from '../assetConfigs'
import { useActiveProfile } from '../hooks/useActiveProfile'

export default function SavingsAccountsPage() {
  const { activeProfileId } = useActiveProfile()
  return <AssetCrudPage config={savingsAccountsConfig} activeProfileId={activeProfileId} />
}
