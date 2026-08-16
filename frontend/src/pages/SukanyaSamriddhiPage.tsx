import { AssetCrudPage } from '../components/assets/AssetCrudPage'
import { sukanyaSamriddhiConfig } from '../assetConfigs'
import { useActiveProfile } from '../hooks/useActiveProfile'

export default function SukanyaSamriddhiPage() {
  const { activeProfileId } = useActiveProfile()
  return <AssetCrudPage config={sukanyaSamriddhiConfig} activeProfileId={activeProfileId} />
}
