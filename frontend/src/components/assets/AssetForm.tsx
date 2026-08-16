import { useMemo, useState } from 'react'
import type { FieldConfig } from '../../types/asset'
import type { AssetRecord } from '../../types/asset'
import type { Profile } from '../../types/api'
import { Input } from '../ui/input'
import { Label } from '../ui/label'
import { Checkbox } from '../ui/checkbox'
import { Button } from '../ui/button'
import { DialogFooter } from '../ui/dialog'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select'
import { useToast } from '../ui/use-toast'

type FormValue = string | boolean

/** Radix Select disallows an empty-string item value, so "Family (all)" (-> null) uses this sentinel. */
const FAMILY_VALUE = '__family__'

function buildInitialState(fields: FieldConfig[], initialValues?: AssetRecord | null): Record<string, FormValue> {
  const state: Record<string, FormValue> = {}
  for (const field of fields) {
    if (field.hidden) continue
    const raw = initialValues ? initialValues[field.key] : undefined

    if (field.type === 'boolean') {
      if (raw !== undefined) state[field.key] = Boolean(raw)
      else state[field.key] = Boolean(field.defaultValue ?? false)
      continue
    }

    if (initialValues) {
      if (raw === null || raw === undefined) {
        state[field.key] = ''
      } else if (field.type === 'datetime') {
        state[field.key] = String(raw).slice(0, 16)
      } else if (field.key === 'profile_id') {
        state[field.key] = String(raw)
      } else {
        state[field.key] = String(raw)
      }
    } else {
      state[field.key] = field.defaultValue !== undefined ? String(field.defaultValue) : ''
    }
  }
  return state
}

export function AssetForm({
  fields,
  initialValues,
  onSubmit,
  onCancel,
  isPending,
  profileOptions,
}: {
  fields: FieldConfig[]
  initialValues?: AssetRecord | null
  onSubmit: (payload: Record<string, unknown>) => void
  onCancel: () => void
  isPending?: boolean
  profileOptions?: Profile[]
}) {
  const visibleFields = useMemo(() => fields.filter((f) => !f.hidden), [fields])
  const [values, setValues] = useState<Record<string, FormValue>>(() => buildInitialState(fields, initialValues))
  const { toast } = useToast()

  function setValue(key: string, value: FormValue) {
    setValues((prev) => ({ ...prev, [key]: value }))
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()

    const missing: string[] = []
    for (const field of visibleFields) {
      if (!field.required) continue
      const v = values[field.key]
      if (v === '' || v === undefined || v === null) missing.push(field.label)
    }
    if (missing.length > 0) {
      toast({
        variant: 'destructive',
        title: 'Missing required fields',
        description: missing.join(', '),
      })
      return
    }

    const payload: Record<string, unknown> = {}
    for (const field of visibleFields) {
      const raw = values[field.key]

      if (field.type === 'boolean') {
        payload[field.key] = Boolean(raw)
        continue
      }

      if (field.key === 'profile_id') {
        // Goals-only case: real visible profile select, "" means family-level (null).
        payload[field.key] = raw === '' ? null : Number(raw)
        continue
      }

      if (field.type === 'number') {
        if (raw === '' || raw === undefined) continue
        payload[field.key] = Number(raw)
        continue
      }

      if (field.type === 'date') {
        if (!raw) continue
        payload[field.key] = raw
        continue
      }

      if (field.type === 'datetime') {
        if (!raw) continue
        payload[field.key] = new Date(raw as string).toISOString()
        continue
      }

      // text / textarea / select
      if (raw === '' && !field.required) continue
      payload[field.key] = raw
    }

    onSubmit(payload)
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      <div className="grid gap-4 sm:grid-cols-2">
        {visibleFields.map((field) => (
          <div
            key={field.key}
            className={field.type === 'textarea' ? 'sm:col-span-2 flex flex-col gap-1.5' : 'flex flex-col gap-1.5'}
          >
            <Label htmlFor={field.key}>
              {field.label}
              {field.required && <span className="text-destructive"> *</span>}
            </Label>

            {field.key === 'profile_id' && !field.hidden ? (
              <Select
                value={values[field.key] === '' || values[field.key] === undefined ? FAMILY_VALUE : String(values[field.key])}
                onValueChange={(v) => setValue(field.key, v === FAMILY_VALUE ? '' : v)}
              >
                <SelectTrigger id={field.key}>
                  <SelectValue placeholder="Family (all)" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value={FAMILY_VALUE}>Family (all)</SelectItem>
                  {(profileOptions ?? []).map((p) => (
                    <SelectItem key={p.id} value={String(p.id)}>
                      {p.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            ) : field.type === 'select' ? (
              <Select value={String(values[field.key] ?? '')} onValueChange={(v) => setValue(field.key, v)}>
                <SelectTrigger id={field.key}>
                  <SelectValue placeholder={`Select ${field.label.toLowerCase()}`} />
                </SelectTrigger>
                <SelectContent>
                  {(field.options ?? []).map((opt) => (
                    <SelectItem key={opt.value} value={opt.value}>
                      {opt.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            ) : field.type === 'boolean' ? (
              <div className="flex h-11 items-center gap-2">
                <Checkbox
                  id={field.key}
                  checked={Boolean(values[field.key])}
                  onCheckedChange={(checked) => setValue(field.key, checked === true)}
                />
              </div>
            ) : field.type === 'textarea' ? (
              <textarea
                id={field.key}
                className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                value={String(values[field.key] ?? '')}
                onChange={(e) => setValue(field.key, e.target.value)}
              />
            ) : field.type === 'number' ? (
              <Input
                id={field.key}
                type="text"
                inputMode="decimal"
                value={String(values[field.key] ?? '')}
                onChange={(e) => setValue(field.key, e.target.value)}
              />
            ) : field.type === 'date' ? (
              <Input
                id={field.key}
                type="date"
                value={String(values[field.key] ?? '')}
                onChange={(e) => setValue(field.key, e.target.value)}
              />
            ) : field.type === 'datetime' ? (
              <Input
                id={field.key}
                type="datetime-local"
                value={String(values[field.key] ?? '')}
                onChange={(e) => setValue(field.key, e.target.value)}
              />
            ) : (
              <Input
                id={field.key}
                type="text"
                value={String(values[field.key] ?? '')}
                onChange={(e) => setValue(field.key, e.target.value)}
              />
            )}
          </div>
        ))}
      </div>

      <DialogFooter>
        <Button type="button" variant="outline" onClick={onCancel} disabled={isPending}>
          Cancel
        </Button>
        <Button type="submit" disabled={isPending}>
          {isPending ? 'Saving…' : 'Save'}
        </Button>
      </DialogFooter>
    </form>
  )
}
