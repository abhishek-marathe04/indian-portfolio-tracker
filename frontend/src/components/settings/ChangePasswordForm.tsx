import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { Label } from '../ui/label'
import { Input } from '../ui/input'
import { Button } from '../ui/button'
import { changePassword } from '../../api/auth'
import { useToast } from '../ui/use-toast'

interface AxiosLikeError {
  response?: { data?: { detail?: string } }
}

export function ChangePasswordForm() {
  const { toast } = useToast()
  const [current, setCurrent] = useState('')
  const [next, setNext] = useState('')
  const [confirm, setConfirm] = useState('')

  const mutation = useMutation({
    mutationFn: () => changePassword(current, next),
    onSuccess: () => {
      toast({ title: 'Password changed' })
      setCurrent('')
      setNext('')
      setConfirm('')
    },
    onError: (err) => {
      const e = err as AxiosLikeError
      toast({ variant: 'destructive', title: 'Could not change password', description: e.response?.data?.detail ?? 'Please try again.' })
    },
  })

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!current || !next || !confirm) {
      toast({ variant: 'destructive', title: 'Missing fields', description: 'All fields are required.' })
      return
    }
    if (next !== confirm) {
      toast({ variant: 'destructive', title: 'Passwords do not match' })
      return
    }
    mutation.mutate()
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Change Password</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="flex max-w-sm flex-col gap-4">
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="current-password">Current Password</Label>
            <Input id="current-password" type="password" value={current} onChange={(e) => setCurrent(e.target.value)} />
          </div>
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="new-password">New Password</Label>
            <Input id="new-password" type="password" value={next} onChange={(e) => setNext(e.target.value)} />
          </div>
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="confirm-password">Confirm New Password</Label>
            <Input id="confirm-password" type="password" value={confirm} onChange={(e) => setConfirm(e.target.value)} />
          </div>
          <Button type="submit" disabled={mutation.isPending}>
            {mutation.isPending ? 'Changing…' : 'Change Password'}
          </Button>
        </form>
      </CardContent>
    </Card>
  )
}
