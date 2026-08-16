import { AssetCrudPage } from '../components/assets/AssetCrudPage'
import { postOfficeConfig } from '../assetConfigs'
import { useActiveProfile } from '../hooks/useActiveProfile'

export default function PostOfficePage() {
  const { activeProfileId } = useActiveProfile()
  return <AssetCrudPage config={postOfficeConfig} activeProfileId={activeProfileId} />
}
