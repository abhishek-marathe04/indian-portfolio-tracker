import { CheckCircle2, CircleAlert, CircleDashed, Loader2 } from 'lucide-react'
import type { BulkFileStatus } from '../../types/api'
import { Badge } from '../ui/badge'

const STATUS_META: Record<BulkFileStatus['status'], { label: string; icon: typeof CheckCircle2; variant: 'default' | 'secondary' | 'destructive' | 'success' }> = {
  queued: { label: 'Queued', icon: CircleDashed, variant: 'secondary' },
  processing: { label: 'Processing', icon: Loader2, variant: 'default' },
  done: { label: 'Done', icon: CheckCircle2, variant: 'success' },
  duplicate: { label: 'Duplicate', icon: CircleAlert, variant: 'secondary' },
  error: { label: 'Error', icon: CircleAlert, variant: 'destructive' },
}

export function BulkProgressList({ files }: { files: BulkFileStatus[] }) {
  if (files.length === 0) return null

  return (
    <ul className="flex flex-col divide-y divide-border rounded-md border border-border">
      {files.map((f) => {
        const meta = STATUS_META[f.status]
        const Icon = meta.icon
        return (
          <li key={f.filename} className="flex flex-col gap-1 p-3 sm:flex-row sm:items-center sm:justify-between">
            <div className="min-w-0">
              <p className="truncate text-sm font-medium">{f.filename}</p>
              {f.message && <p className="truncate text-xs text-muted-foreground">{f.message}</p>}
              {(f.folios_found !== undefined || f.new_transactions !== undefined) && (
                <p className="text-xs text-muted-foreground">
                  {f.folios_found !== undefined && `${f.folios_found} folios`}
                  {f.folios_found !== undefined && f.new_transactions !== undefined && ' · '}
                  {f.new_transactions !== undefined && `${f.new_transactions} new transactions`}
                </p>
              )}
            </div>
            <Badge variant={meta.variant} className="flex w-fit shrink-0 items-center gap-1">
              <Icon className={f.status === 'processing' ? 'h-3 w-3 animate-spin' : 'h-3 w-3'} />
              {meta.label}
            </Badge>
          </li>
        )
      })}
    </ul>
  )
}
