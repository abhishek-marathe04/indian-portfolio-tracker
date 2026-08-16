import { AssetCrudPage } from '../components/assets/AssetCrudPage'
import { depositsConfig } from '../assetConfigs'
import { useActiveProfile } from '../hooks/useActiveProfile'

export default function DepositsPage() {
  const { activeProfileId } = useActiveProfile()
  return <AssetCrudPage config={depositsConfig} activeProfileId={activeProfileId} />
}
