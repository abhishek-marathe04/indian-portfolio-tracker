import { useMutation, useQueryClient } from '@tanstack/react-query'
import { RefreshCw } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { Button } from '../ui/button'
import { refreshPrices } from '../../api/analytics'
import { useToast } from '../ui/use-toast'

interface AxiosLikeError {
  response?: { data?: { detail?: string } }
}

export function RefreshPricesButton() {
  const { toast } = useToast()
  const queryClient = useQueryClient()

  const mutation = useMutation({
    mutationFn: refreshPrices,
    onSuccess: (data) => {
      toast({ title: 'Prices refreshed', description: data.message })
      queryClient.invalidateQueries({ queryKey: ['assets', 'mutual-funds'] })
      queryClient.invalidateQueries({ queryKey: ['net-worth'] })
      queryClient.invalidateQueries({ queryKey: ['allocation'] })
    },
    onError: (err) => {
      const e = err as AxiosLikeError
      toast({ variant: 'destructive', title: 'Refresh failed', description: e.response?.data?.detail ?? 'Please try again.' })
    },
  })

  return (
    <Card>
      <CardHeader>
        <CardTitle>Refresh Prices</CardTitle>
        <CardDescription>Fetches the latest NAVs / prices for holdings that support live pricing. Can take a few seconds.</CardDescription>
      </CardHeader>
      <CardContent>
        <Button onClick={() => mutation.mutate()} disabled={mutation.isPending}>
          <RefreshCw className={mutation.isPending ? 'h-4 w-4 animate-spin' : 'h-4 w-4'} />
          {mutation.isPending ? 'Refreshing…' : 'Refresh Prices'}
        </Button>
      </CardContent>
    </Card>
  )
}
