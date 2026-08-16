import { AssetCrudPage } from '../components/assets/AssetCrudPage'
import { GoalProgressBar } from '../components/assets/GoalProgressBar'
import { goalsConfig } from '../assetConfigs'
import { useActiveProfile } from '../hooks/useActiveProfile'
import type { AssetRecord } from '../types/asset'

export default function GoalsPage() {
  const { activeProfileId } = useActiveProfile()

  return (
    <AssetCrudPage
      config={goalsConfig}
      activeProfileId={activeProfileId}
      valueColumnRenderer={(row: AssetRecord) => (
        <GoalProgressBar current={Number(row.current_value ?? 0)} target={Number(row.target_amount ?? 0)} />
      )}
    />
  )
}
