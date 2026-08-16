import { useCallback, useMemo } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { listProfiles } from '../api/profiles'

/**
 * Active profile selection lives in the `?profile=` URL search param (not React
 * context) so it survives a refresh and is shared across Dashboard/Portfolio pages.
 * `null` means "All Profiles (Consolidated)".
 */
export function useActiveProfile() {
  const [searchParams, setSearchParams] = useSearchParams()

  const profilesQuery = useQuery({
    queryKey: ['profiles'],
    queryFn: listProfiles,
  })

  const raw = searchParams.get('profile')
  const activeProfileId = raw !== null && raw !== '' ? Number(raw) : null

  const setActiveProfileId = useCallback(
    (id: number | null) => {
      setSearchParams(
        (prev) => {
          const next = new URLSearchParams(prev)
          if (id === null) {
            next.delete('profile')
          } else {
            next.set('profile', String(id))
          }
          return next
        },
        { replace: true },
      )
    },
    [setSearchParams],
  )

  const activeProfile = useMemo(
    () => profilesQuery.data?.find((p) => p.id === activeProfileId) ?? null,
    [profilesQuery.data, activeProfileId],
  )

  return {
    profiles: profilesQuery.data ?? [],
    profilesLoading: profilesQuery.isLoading,
    activeProfileId,
    activeProfile,
    setActiveProfileId,
  }
}
