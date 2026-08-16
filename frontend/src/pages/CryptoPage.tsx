import { AssetCrudPage } from '../components/assets/AssetCrudPage'
import { cryptoConfig } from '../assetConfigs'
import { useActiveProfile } from '../hooks/useActiveProfile'

export default function CryptoPage() {
  const { activeProfileId } = useActiveProfile()
  return <AssetCrudPage config={cryptoConfig} activeProfileId={activeProfileId} />
}
