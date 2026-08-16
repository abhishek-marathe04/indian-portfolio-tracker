import { AssetCrudPage } from '../components/assets/AssetCrudPage'
import { goldConfig } from '../assetConfigs'
import { useActiveProfile } from '../hooks/useActiveProfile'

export default function GoldPage() {
  const { activeProfileId } = useActiveProfile()
  return <AssetCrudPage config={goldConfig} activeProfileId={activeProfileId} />
}
