import { AssetCrudPage } from '../components/assets/AssetCrudPage'
import { providentFundsConfig } from '../assetConfigs'
import { useActiveProfile } from '../hooks/useActiveProfile'

export default function ProvidentFundsPage() {
  const { activeProfileId } = useActiveProfile()
  return <AssetCrudPage config={providentFundsConfig} activeProfileId={activeProfileId} />
}
