import { useQuery } from '@tanstack/react-query'
import { AlertTriangle, Clock } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { Badge } from '../ui/badge'
import { EmptyState } from '../common/EmptyState'
import { LoadingSpinner } from '../common/LoadingSpinner'
import { useMaturityAlerts, MATURITY_WINDOW_DAYS } from '../../hooks/useMaturityAlerts'
import type { MaturityAlert } from '../../hooks/useMaturityAlerts'
import { listProfiles } from '../../api/profiles'
import { formatDate, formatINR } from '../../lib/formatters'

function AlertRow({ alert, profileName }: { alert: MaturityAlert; profileName: string }) {
  return (
    <li className="flex flex-col gap-1 border-b border-border py-3 last:border-0 sm:flex-row sm:items-center sm:justify-between">
      <div className="min-w-0">
        <div className="flex flex-wrap items-center gap-2">
          <span className="font-medium">{alert.label}</span>
          <Badge variant="outline" className="text-[10px]">
            {alert.categoryLabel}
          </Badge>
        </div>
        <p className="text-xs text-muted-foreground">{profileName}</p>
      </div>
      <div className="flex shrink-0 items-center gap-4 text-sm">
        <span className={alert.isOverdue ? 'font-medium text-loss' : 'text-muted-foreground'}>
          {formatDate(alert.maturityDate)}
        </span>
        <span className="font-medium tabular-nums">{formatINR(alert.amount)}</span>
      </div>
    </li>
  )
}

export function MaturityAlertsList() {
  const { upcoming, overdue, isLoading, isError } = useMaturityAlerts()
  const profilesQuery = useQuery({ queryKey: ['profiles'], queryFn: listProfiles })

  function profileName(id: number | null): string {
    if (id === null) return 'Family'
    return profilesQuery.data?.find((p) => p.id === id)?.name ?? `Profile #${id}`
  }

  if (isLoading) return <LoadingSpinner />
  if (isError) return <p className="text-sm text-destructive">Failed to load maturity alerts.</p>

  return (
    <div className="flex flex-col gap-6">
      <Card className="border-loss/30">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-loss">
            <AlertTriangle className="h-5 w-5" />
            Overdue
          </CardTitle>
        </CardHeader>
        <CardContent>
          {overdue.length === 0 ? (
            <p className="text-sm text-muted-foreground">Nothing overdue.</p>
          ) : (
            <ul>
              {overdue.map((a) => (
                <AlertRow key={a.key} alert={a} profileName={profileName(a.profileId)} />
              ))}
            </ul>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="h-5 w-5" />
            Upcoming (next {MATURITY_WINDOW_DAYS} days)
          </CardTitle>
        </CardHeader>
        <CardContent>
          {upcoming.length === 0 ? (
            <EmptyState title="Nothing maturing soon" description={`No deposits, provident funds, Sukanya Samriddhi or post office schemes mature in the next ${MATURITY_WINDOW_DAYS} days.`} />
          ) : (
            <ul>
              {upcoming.map((a) => (
                <AlertRow key={a.key} alert={a} profileName={profileName(a.profileId)} />
              ))}
            </ul>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
