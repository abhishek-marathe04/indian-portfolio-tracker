import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Plus } from 'lucide-react'
import { PageHeader } from '../components/common/PageHeader'
import { LoadingSpinner } from '../components/common/LoadingSpinner'
import { EmptyState } from '../components/common/EmptyState'
import { ConfirmDeleteDialog } from '../components/common/ConfirmDeleteDialog'
import { Button } from '../components/ui/button'
import { Badge } from '../components/ui/badge'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/table'
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from '../components/ui/dialog'
import { Label } from '../components/ui/label'
import { Input } from '../components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select'
import { useToast } from '../components/ui/use-toast'
import { createProfile, deleteProfile, listProfiles, updateProfile } from '../api/profiles'
import type { Profile, ProfileInput, Relationship } from '../types/api'
import { formatDate } from '../lib/formatters'

const RELATIONSHIPS: Relationship[] = ['self', 'spouse', 'child', 'parent', 'other']

interface AxiosLikeError {
  response?: { data?: { detail?: string } }
}

function emptyForm(): ProfileInput {
  return { name: '', relationship: 'self', date_of_birth: '', pan_number: '' }
}

export default function FamilyProfilesPage() {
  const { toast } = useToast()
  const queryClient = useQueryClient()
  const profilesQuery = useQuery({ queryKey: ['profiles'], queryFn: listProfiles })

  const [dialogOpen, setDialogOpen] = useState(false)
  const [editing, setEditing] = useState<Profile | null>(null)
  const [form, setForm] = useState<ProfileInput>(emptyForm())
  const [deleteTarget, setDeleteTarget] = useState<Profile | null>(null)

  const invalidate = () => queryClient.invalidateQueries({ queryKey: ['profiles'] })

  const createMutation = useMutation({
    mutationFn: (data: ProfileInput) => createProfile(data),
    onSuccess: () => {
      invalidate()
      toast({ title: 'Profile added' })
      closeDialog()
    },
    onError: (err) => {
      const e = err as AxiosLikeError
      toast({ variant: 'destructive', title: 'Could not save profile', description: e.response?.data?.detail ?? 'Please try again.' })
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<ProfileInput> }) => updateProfile(id, data),
    onSuccess: () => {
      invalidate()
      toast({ title: 'Profile updated' })
      closeDialog()
    },
    onError: (err) => {
      const e = err as AxiosLikeError
      toast({ variant: 'destructive', title: 'Could not save profile', description: e.response?.data?.detail ?? 'Please try again.' })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteProfile(id),
    onSuccess: () => {
      invalidate()
      toast({ title: 'Profile deleted' })
      setDeleteTarget(null)
    },
    onError: (err) => {
      const e = err as AxiosLikeError
      toast({ variant: 'destructive', title: 'Could not delete profile', description: e.response?.data?.detail ?? 'Please try again.' })
    },
  })

  function closeDialog() {
    setDialogOpen(false)
    setEditing(null)
    setForm(emptyForm())
  }

  function handleAddClick() {
    setEditing(null)
    setForm(emptyForm())
    setDialogOpen(true)
  }

  function handleEditClick(profile: Profile) {
    setEditing(profile)
    setForm({
      name: profile.name,
      relationship: profile.relationship,
      date_of_birth: profile.date_of_birth ?? '',
      pan_number: profile.pan_number ?? '',
    })
    setDialogOpen(true)
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!form.name) {
      toast({ variant: 'destructive', title: 'Name is required' })
      return
    }

    // Omit blank optionals rather than sending empty strings — matches the
    // asset-form convention of never clobbering existing values with blanks.
    const payload: Partial<ProfileInput> = { name: form.name, relationship: form.relationship }
    if (form.date_of_birth) payload.date_of_birth = form.date_of_birth
    if (form.pan_number) payload.pan_number = form.pan_number

    if (editing) {
      updateMutation.mutate({ id: editing.id, data: payload })
    } else {
      createMutation.mutate(payload as ProfileInput)
    }
  }

  const isSaving = createMutation.isPending || updateMutation.isPending

  return (
    <div>
      <PageHeader
        title="Family Profiles"
        description="Manage the family members whose portfolios you're tracking."
        action={
          <Button onClick={handleAddClick}>
            <Plus className="h-4 w-4" />
            Add Profile
          </Button>
        }
      />

      {profilesQuery.isLoading ? (
        <LoadingSpinner />
      ) : profilesQuery.isError ? (
        <p className="text-sm text-destructive">Failed to load profiles.</p>
      ) : !profilesQuery.data || profilesQuery.data.length === 0 ? (
        <EmptyState title="No profiles yet" description="Add a profile to start tracking a portfolio." />
      ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Relationship</TableHead>
              <TableHead>Date of Birth</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {profilesQuery.data.map((p) => (
              <TableRow key={p.id}>
                <TableCell className="font-medium">{p.name}</TableCell>
                <TableCell>
                  <Badge variant="secondary" className="capitalize">
                    {p.relationship}
                  </Badge>
                </TableCell>
                <TableCell>{formatDate(p.date_of_birth)}</TableCell>
                <TableCell className="text-right">
                  <div className="flex justify-end gap-1">
                    <Button variant="ghost" size="sm" onClick={() => handleEditClick(p)}>
                      Edit
                    </Button>
                    <Button variant="ghost" size="sm" onClick={() => setDeleteTarget(p)}>
                      Delete
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}

      <Dialog open={dialogOpen} onOpenChange={(open) => (open ? setDialogOpen(true) : closeDialog())}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{editing ? 'Edit' : 'Add'} Profile</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="profile-name">Name *</Label>
              <Input id="profile-name" value={form.name} onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))} />
            </div>
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="profile-relationship">Relationship</Label>
              <Select value={form.relationship} onValueChange={(v) => setForm((f) => ({ ...f, relationship: v as Relationship }))}>
                <SelectTrigger id="profile-relationship">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {RELATIONSHIPS.map((r) => (
                    <SelectItem key={r} value={r} className="capitalize">
                      {r}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="profile-dob">Date of Birth</Label>
              <Input
                id="profile-dob"
                type="date"
                value={form.date_of_birth ?? ''}
                onChange={(e) => setForm((f) => ({ ...f, date_of_birth: e.target.value }))}
              />
            </div>
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="profile-pan">PAN Number</Label>
              <Input
                id="profile-pan"
                value={form.pan_number ?? ''}
                onChange={(e) => setForm((f) => ({ ...f, pan_number: e.target.value }))}
              />
              <p className="text-xs text-muted-foreground">Encrypted at rest.</p>
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={closeDialog} disabled={isSaving}>
                Cancel
              </Button>
              <Button type="submit" disabled={isSaving}>
                {isSaving ? 'Saving…' : 'Save'}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      <ConfirmDeleteDialog
        open={deleteTarget !== null}
        onOpenChange={(open) => !open && setDeleteTarget(null)}
        onConfirm={() => deleteTarget && deleteMutation.mutate(deleteTarget.id)}
        itemLabel="profile"
        isPending={deleteMutation.isPending}
      />
    </div>
  )
}
