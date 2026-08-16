import type { ReactNode } from 'react'
import { Pencil, Trash2 } from 'lucide-react'
import type { AssetRecord, FieldConfig } from '../../types/asset'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../ui/table'
import { Button } from '../ui/button'
import { Badge } from '../ui/badge'
import { formatDate, formatINR, formatNumber, formatPct } from '../../lib/formatters'
import { EmptyState } from '../common/EmptyState'

function renderCellValue(field: FieldConfig, row: AssetRecord): ReactNode {
  const value = row[field.key]

  if (value === null || value === undefined || value === '') return <span className="text-muted-foreground">—</span>

  if (field.type === 'boolean') {
    return <Badge variant={value ? 'success' : 'secondary'}>{value ? 'Yes' : 'No'}</Badge>
  }
  if (field.type === 'date' || field.type === 'datetime') {
    return formatDate(String(value))
  }
  if (field.type === 'number') {
    const num = Number(value)
    if (field.format === 'currency') return formatINR(num)
    if (field.format === 'percent') return formatPct(num)
    return formatNumber(num)
  }
  if (field.type === 'select' && field.options) {
    const opt = field.options.find((o) => o.value === String(value))
    return opt?.label ?? String(value)
  }
  return String(value)
}

export function AssetTable({
  fields,
  rows,
  onEdit,
  onDelete,
  valueColumnRenderer,
}: {
  fields: FieldConfig[]
  rows: AssetRecord[]
  onEdit: (row: AssetRecord) => void
  onDelete: (row: AssetRecord) => void
  valueColumnRenderer?: (row: AssetRecord) => ReactNode
}) {
  const columns = fields.filter((f) => !f.hidden && f.showInTable !== false)

  if (rows.length === 0) {
    return <EmptyState title="No records yet" description="Add your first record using the button above." />
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          {columns.map((f) => (
            <TableHead key={f.key}>{f.label}</TableHead>
          ))}
          <TableHead className="text-right">Actions</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {rows.map((row) => (
          <TableRow key={row.id}>
            {columns.map((f) => (
              <TableCell key={f.key}>
                {f.key === 'current_value' && valueColumnRenderer ? valueColumnRenderer(row) : renderCellValue(f, row)}
              </TableCell>
            ))}
            <TableCell className="text-right">
              <div className="flex justify-end gap-1">
                <Button variant="ghost" size="icon" onClick={() => onEdit(row)} aria-label="Edit">
                  <Pencil className="h-4 w-4" />
                </Button>
                <Button variant="ghost" size="icon" onClick={() => onDelete(row)} aria-label="Delete">
                  <Trash2 className="h-4 w-4 text-destructive" />
                </Button>
              </div>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}
