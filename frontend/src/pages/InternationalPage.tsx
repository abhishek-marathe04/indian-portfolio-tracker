import { AssetCrudPage } from '../components/assets/AssetCrudPage'
import { internationalConfig } from '../assetConfigs'
import { useActiveProfile } from '../hooks/useActiveProfile'

export default function InternationalPage() {
  const { activeProfileId } = useActiveProfile()
  return <AssetCrudPage config={internationalConfig} activeProfileId={activeProfileId} />
}
