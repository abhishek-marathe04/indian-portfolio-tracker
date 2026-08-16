import { useQuery } from '@tanstack/react-query'
import { fetchCurrentUser } from '../api/auth'

export function useAuth() {
  return useQuery({
    queryKey: ['auth', 'me'],
    queryFn: fetchCurrentUser,
    retry: false,
  })
}
