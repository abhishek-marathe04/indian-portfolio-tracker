import { AssetCrudPage } from '../components/assets/AssetCrudPage'
import { realEstateConfig } from '../assetConfigs'
import { useActiveProfile } from '../hooks/useActiveProfile'

export default function RealEstatePage() {
  const { activeProfileId } = useActiveProfile()
  return <AssetCrudPage config={realEstateConfig} activeProfileId={activeProfileId} />
}
