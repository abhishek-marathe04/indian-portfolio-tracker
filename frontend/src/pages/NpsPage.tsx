import { AssetCrudPage } from '../components/assets/AssetCrudPage'
import { npsConfig } from '../assetConfigs'
import { useActiveProfile } from '../hooks/useActiveProfile'

export default function NpsPage() {
  const { activeProfileId } = useActiveProfile()
  return <AssetCrudPage config={npsConfig} activeProfileId={activeProfileId} />
}
