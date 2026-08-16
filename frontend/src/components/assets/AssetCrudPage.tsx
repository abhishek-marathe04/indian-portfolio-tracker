import type { ReactNode } from 'react'
import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Plus } from 'lucide-react'
import type { AssetRecord, AssetTypeConfig } from '../../types/asset'
import { listProfiles } from '../../api/profiles'
import { AssetTable } from './AssetTable'
import { AssetForm } from './AssetForm'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../ui/dialog'
import { Button } from '../ui/button'
import { PageHeader } from '../common/PageHeader'
import { LoadingSpinner } from '../common/LoadingSpinner'
import { ConfirmDeleteDialog } from '../common/ConfirmDeleteDialog'
import { useToast } from '../ui/use-toast'

interface AxiosLikeError {
  response?: { data?: { detail?: string } }
  message?: string
}

function extractErrorMessage(err: unknown, fallback: string): string {
  const e = err as AxiosLikeError
  return e?.response?.data?.detail ?? e?.message ?? fallback
}

export function AssetCrudPage({
  config,
  activeProfileId,
  valueColumnRenderer,
  title,
  description,
}: {
  config: AssetTypeConfig
  activeProfileId: number | null
  valueColumnRenderer?: (row: AssetRecord) => ReactNode
  title?: string
  description?: string
}) {
  const queryClient = useQueryClient()
  const { toast } = useToast()
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editingRow, setEditingRow] = useState<AssetRecord | null>(null)
  const [deleteTarget, setDeleteTarget] = useState<AssetRecord | null>(null)

  const profileIdField = config.fields.find((f) => f.key === 'profile_id')
  const profileRequiredForCreate = profileIdField ? profileIdField.required !== false : false

  const profilesQuery = useQuery({ queryKey: ['profiles'], queryFn: listProfiles })

  const listQuery = useQuery({
    queryKey: ['assets', config.resourcePath, activeProfileId],
    queryFn: () => config.api.list(activeProfileId),
  })

  const invalidate = () => queryClient.invalidateQueries({ queryKey: ['assets', config.resourcePath] })

  const createMutation = useMutation({
    mutationFn: (data: Record<string, unknown>) => config.api.create(data),
    onSuccess: () => {
      invalidate()
      toast({ title: `${config.singularLabel} added` })
      closeDialog()
    },
    onError: (err) => {
      toast({ variant: 'destructive', title: 'Could not save', description: extractErrorMessage(err, 'Please try again.') })
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Record<string, unknown> }) => config.api.update(id, data),
    onSuccess: () => {
      invalidate()
      toast({ title: `${config.singularLabel} updated` })
      closeDialog()
    },
    onError: (err) => {
      toast({ variant: 'destructive', title: 'Could not save', description: extractErrorMessage(err, 'Please try again.') })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => config.api.remove(id),
    onSuccess: () => {
      invalidate()
      toast({ title: `${config.singularLabel} deleted` })
      setDeleteTarget(null)
    },
    onError: (err) => {
      toast({ variant: 'destructive', title: 'Could not delete', description: extractErrorMessage(err, 'Please try again.') })
    },
  })

  function closeDialog() {
    setDialogOpen(false)
    setEditingRow(null)
  }

  function handleAddClick() {
    setEditingRow(null)
    setDialogOpen(true)
  }

  function handleEditClick(row: AssetRecord) {
    setEditingRow(row)
    setDialogOpen(true)
  }

  function handleFormSubmit(payload: Record<string, unknown>) {
    const finalPayload = { ...payload }

    // Hidden profile_id fields (14 of 15 resources) are never rendered in the
    // form — inject the page's active profile on create. Updates omit it so
    // an existing record's profile assignment is left untouched.
    if (profileIdField?.hidden && !editingRow) {
      finalPayload.profile_id = activeProfileId
    }

    if (editingRow) {
      updateMutation.mutate({ id: editingRow.id, data: finalPayload })
    } else {
      createMutation.mutate(finalPayload)
    }
  }

  const addDisabled = activeProfileId === null && profileRequiredForCreate
  const isSaving = createMutation.isPending || updateMutation.isPending

  return (
    <div>
      <PageHeader
        title={title ?? config.title}
        description={description}
        action={
          <div className="flex flex-col items-end gap-1">
            <Button onClick={handleAddClick} disabled={addDisabled}>
              <Plus className="h-4 w-4" />
              Add {config.singularLabel}
            </Button>
            {addDisabled && <span className="text-xs text-muted-foreground">Select a profile to add records</span>}
          </div>
        }
      />

      {listQuery.isLoading ? (
        <LoadingSpinner />
      ) : listQuery.isError ? (
        <p className="text-sm text-destructive">Failed to load {config.title.toLowerCase()}.</p>
      ) : (
        <AssetTable
          fields={config.fields}
          rows={listQuery.data ?? []}
          onEdit={handleEditClick}
          onDelete={(row) => setDeleteTarget(row)}
          valueColumnRenderer={valueColumnRenderer}
        />
      )}

      <Dialog open={dialogOpen} onOpenChange={(open) => (open ? setDialogOpen(true) : closeDialog())}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {editingRow ? 'Edit' : 'Add'} {config.singularLabel}
            </DialogTitle>
          </DialogHeader>
          <AssetForm
            fields={config.fields}
            initialValues={editingRow}
            onSubmit={handleFormSubmit}
            onCancel={closeDialog}
            isPending={isSaving}
            profileOptions={profilesQuery.data}
          />
        </DialogContent>
      </Dialog>

      <ConfirmDeleteDialog
        open={deleteTarget !== null}
        onOpenChange={(open) => !open && setDeleteTarget(null)}
        onConfirm={() => deleteTarget && deleteMutation.mutate(deleteTarget.id)}
        itemLabel={config.singularLabel}
        isPending={deleteMutation.isPending}
      />
    </div>
  )
}
