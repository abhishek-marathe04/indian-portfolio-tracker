import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select'
import { Badge } from '../ui/badge'
import { useActiveProfile } from '../../hooks/useActiveProfile'

const ALL_VALUE = 'all'

export function ProfileSwitcher() {
  const { profiles, activeProfileId, setActiveProfileId } = useActiveProfile()

  return (
    <Select
      value={activeProfileId === null ? ALL_VALUE : String(activeProfileId)}
      onValueChange={(v) => setActiveProfileId(v === ALL_VALUE ? null : Number(v))}
    >
      <SelectTrigger className="w-full sm:w-64">
        <SelectValue placeholder="Select profile" />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value={ALL_VALUE}>All Profiles (Consolidated)</SelectItem>
        {profiles.map((p) => (
          <SelectItem key={p.id} value={String(p.id)}>
            <span className="flex items-center gap-2">
              {p.name}
              <Badge variant="secondary" className="text-[10px] capitalize">
                {p.relationship}
              </Badge>
            </span>
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  )
}
