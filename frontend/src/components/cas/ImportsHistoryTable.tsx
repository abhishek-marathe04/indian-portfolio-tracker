import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../ui/table'
import { fetchImports } from '../../api/cas'
import { formatDate } from '../../lib/formatters'
import { LoadingSpinner } from '../common/LoadingSpinner'
import { EmptyState } from '../common/EmptyState'

export function ImportsHistoryTable() {
  const { data, isLoading, isError } = useQuery({ queryKey: ['cas', 'imports'], queryFn: fetchImports })

  return (
    <Card>
      <CardHeader>
        <CardTitle>Import History</CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <LoadingSpinner />
        ) : isError ? (
          <p className="text-sm text-destructive">Failed to load import history.</p>
        ) : !data || data.length === 0 ? (
          <EmptyState title="No imports yet" description="Uploaded CAS files will appear here." />
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Filename</TableHead>
                <TableHead>Size</TableHead>
                <TableHead>Uploaded</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.map((imp) => (
                <TableRow key={imp.filename}>
                  <TableCell className="max-w-[240px] truncate">{imp.filename}</TableCell>
                  <TableCell>{imp.size_kb.toFixed(1)} KB</TableCell>
                  <TableCell>{formatDate(imp.uploaded_at)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  )
}
