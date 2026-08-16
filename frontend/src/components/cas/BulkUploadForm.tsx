import { useEffect, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { Label } from '../ui/label'
import { Input } from '../ui/input'
import { Button } from '../ui/button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select'
import { listProfiles } from '../../api/profiles'
import { bulkUploadCas, fetchBulkStatus } from '../../api/cas'
import type { BulkStatusResponse } from '../../types/api'
import { BulkProgressList } from './BulkProgressList'
import { useToast } from '../ui/use-toast'

const POLL_INTERVAL_MS = 1500

interface AxiosLikeError {
  response?: { data?: { detail?: string } }
}

export function BulkUploadForm() {
  const { toast } = useToast()
  const queryClient = useQueryClient()
  const profilesQuery = useQuery({ queryKey: ['profiles'], queryFn: listProfiles })

  const [files, setFiles] = useState<File[]>([])
  const [password, setPassword] = useState('')
  const [profileId, setProfileId] = useState<string>('')
  const [jobId, setJobId] = useState<string | null>(null)
  const [status, setStatus] = useState<BulkStatusResponse | null>(null)

  const uploadMutation = useMutation({
    mutationFn: () => bulkUploadCas(files, password, Number(profileId)),
    onSuccess: (data) => {
      setJobId(data.job_id)
      setStatus(null)
      toast({ title: 'Bulk upload started', description: data.message })
    },
    onError: (err) => {
      const e = err as AxiosLikeError
      toast({ variant: 'destructive', title: 'Upload failed', description: e.response?.data?.detail ?? 'Please try again.' })
    },
  })

  useEffect(() => {
    if (!jobId) return
    if (status?.status === 'complete') return

    let cancelled = false
    const interval = setInterval(async () => {
      try {
        const data = await fetchBulkStatus(jobId)
        if (cancelled) return
        setStatus(data)
        if (data.status === 'complete') {
          clearInterval(interval)
          queryClient.invalidateQueries({ queryKey: ['cas', 'imports'] })
          queryClient.invalidateQueries({ queryKey: ['assets'] })
          toast({ title: 'Bulk upload complete', description: `${data.total_new_transactions} new transactions imported.` })
        }
      } catch {
        // transient poll failure — keep trying until the interval is cleared
      }
    }, POLL_INTERVAL_MS)

    return () => {
      cancelled = true
      clearInterval(interval)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [jobId, status?.status])

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (files.length === 0 || !password || !profileId) {
      toast({ variant: 'destructive', title: 'Missing fields', description: 'Files, password and profile are all required.' })
      return
    }
    uploadMutation.mutate()
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Bulk CAS Upload</CardTitle>
        <CardDescription>Upload multiple CAS PDFs at once, sharing one password.</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="bulk-files">CAS PDFs</Label>
            <Input
              id="bulk-files"
              type="file"
              accept="application/pdf"
              multiple
              onChange={(e) => setFiles(e.target.files ? Array.from(e.target.files) : [])}
            />
            {files.length > 0 && <p className="text-xs text-muted-foreground">{files.length} file(s) selected</p>}
          </div>
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="bulk-password">Password (shared)</Label>
            <Input id="bulk-password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
            <p className="text-xs text-muted-foreground">PAN + DOB in DDMMYYYY format</p>
          </div>
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="bulk-profile">Profile</Label>
            <Select value={profileId} onValueChange={setProfileId}>
              <SelectTrigger id="bulk-profile">
                <SelectValue placeholder="Select profile" />
              </SelectTrigger>
              <SelectContent>
                {(profilesQuery.data ?? []).map((p) => (
                  <SelectItem key={p.id} value={String(p.id)}>
                    {p.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <Button type="submit" disabled={uploadMutation.isPending || (status !== null && status.status === 'running')}>
            {uploadMutation.isPending ? 'Starting…' : 'Upload All'}
          </Button>
        </form>

        {status && (
          <div className="mt-5 flex flex-col gap-3">
            <p className="text-sm text-muted-foreground">
              {status.processed} / {status.total_files} processed
              {status.status === 'complete' ? ' · complete' : ' · in progress…'}
            </p>
            <BulkProgressList files={status.files} />
          </div>
        )}
      </CardContent>
    </Card>
  )
}
