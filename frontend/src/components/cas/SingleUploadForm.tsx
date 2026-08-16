import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { Label } from '../ui/label'
import { Input } from '../ui/input'
import { Button } from '../ui/button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select'
import { listProfiles } from '../../api/profiles'
import { uploadCas } from '../../api/cas'
import type { CasUploadResult } from '../../types/api'
import { useToast } from '../ui/use-toast'

interface AxiosLikeError {
  response?: { data?: { detail?: string } }
}

export function SingleUploadForm() {
  const { toast } = useToast()
  const queryClient = useQueryClient()
  const profilesQuery = useQuery({ queryKey: ['profiles'], queryFn: listProfiles })

  const [file, setFile] = useState<File | null>(null)
  const [password, setPassword] = useState('')
  const [profileId, setProfileId] = useState<string>('')
  const [result, setResult] = useState<CasUploadResult | null>(null)

  const mutation = useMutation({
    mutationFn: () => uploadCas(file as File, password, Number(profileId)),
    onSuccess: (data) => {
      setResult(data)
      toast({ title: 'CAS uploaded', description: data.message ?? 'Processed successfully.' })
      queryClient.invalidateQueries({ queryKey: ['cas', 'imports'] })
      queryClient.invalidateQueries({ queryKey: ['assets'] })
    },
    onError: (err) => {
      const e = err as AxiosLikeError
      toast({ variant: 'destructive', title: 'Upload failed', description: e.response?.data?.detail ?? 'Please try again.' })
    },
  })

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!file || !password || !profileId) {
      toast({ variant: 'destructive', title: 'Missing fields', description: 'File, password and profile are all required.' })
      return
    }
    setResult(null)
    mutation.mutate()
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Single CAS Upload</CardTitle>
        <CardDescription>Upload one Consolidated Account Statement PDF.</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="cas-file">CAS PDF</Label>
            <Input
              id="cas-file"
              type="file"
              accept="application/pdf"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            />
          </div>
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="cas-password">Password</Label>
            <Input
              id="cas-password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <p className="text-xs text-muted-foreground">PAN + DOB in DDMMYYYY format</p>
          </div>
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="cas-profile">Profile</Label>
            <Select value={profileId} onValueChange={setProfileId}>
              <SelectTrigger id="cas-profile">
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
          <Button type="submit" disabled={mutation.isPending}>
            {mutation.isPending ? 'Uploading…' : 'Upload'}
          </Button>
        </form>

        {result && (
          <div className="mt-5 rounded-md border border-border bg-muted/40 p-4 text-sm">
            <p className="mb-2 font-medium">{result.message ?? 'Upload complete'}</p>
            <dl className="grid grid-cols-2 gap-x-4 gap-y-1.5">
              {result.investor_name && (
                <>
                  <dt className="text-muted-foreground">Investor</dt>
                  <dd>{result.investor_name}</dd>
                </>
              )}
              {result.cas_type && (
                <>
                  <dt className="text-muted-foreground">CAS Type</dt>
                  <dd>{result.cas_type}</dd>
                </>
              )}
              {result.folios_found !== undefined && (
                <>
                  <dt className="text-muted-foreground">Folios Found</dt>
                  <dd>{result.folios_found}</dd>
                </>
              )}
              {result.new_folios !== undefined && (
                <>
                  <dt className="text-muted-foreground">New Folios</dt>
                  <dd>{result.new_folios}</dd>
                </>
              )}
              {result.updated_folios !== undefined && (
                <>
                  <dt className="text-muted-foreground">Updated Folios</dt>
                  <dd>{result.updated_folios}</dd>
                </>
              )}
              {result.new_transactions !== undefined && (
                <>
                  <dt className="text-muted-foreground">New Transactions</dt>
                  <dd>{result.new_transactions}</dd>
                </>
              )}
            </dl>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
