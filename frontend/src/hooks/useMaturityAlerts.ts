import { useMemo } from 'react'
import { useQueries } from '@tanstack/react-query'
import { differenceInCalendarDays, parseISO } from 'date-fns'
import { makeAssetApi } from '../api/assets'
import type { AssetRecord } from '../types/asset'

/** Alerts fire for maturities within this many days from today. Easy to tune later. */
export const MATURITY_WINDOW_DAYS = 90

export type MaturityCategory = 'deposits' | 'provident-funds' | 'sukanya-samriddhi' | 'post-office'

export interface MaturityAlert {
  key: string
  category: MaturityCategory
  categoryLabel: string
  label: string
  profileId: number | null
  maturityDate: string
  amount: number | null
  isOverdue: boolean
  daysUntil: number
}

const depositsApi = makeAssetApi('deposits')
const providentFundsApi = makeAssetApi('provident-funds')
const sukanyaApi = makeAssetApi('sukanya-samriddhi')
const postOfficeApi = makeAssetApi('post-office')

const CATEGORY_LABELS: Record<MaturityCategory, string> = {
  deposits: 'Fixed / Recurring Deposit',
  'provident-funds': 'Provident Fund',
  'sukanya-samriddhi': 'Sukanya Samriddhi',
  'post-office': 'Post Office Scheme',
}

function num(v: unknown): number | null {
  return typeof v === 'number' && !Number.isNaN(v) ? v : null
}

function str(v: unknown): string {
  return typeof v === 'string' && v.length > 0 ? v : ''
}

function toAlert(row: AssetRecord, category: MaturityCategory, today: Date): MaturityAlert | null {
  const maturityDate = str(row.maturity_date)
  if (!maturityDate) return null

  let amount: number | null = null
  let label = ''
  if (category === 'deposits') {
    amount = num(row.maturity_amount) ?? num(row.principal_amount)
    label = str(row.bank_name) || str(row.type) || 'Deposit'
  } else if (category === 'post-office') {
    amount = num(row.maturity_amount) ?? num(row.principal_amount)
    label = str(row.scheme_type) || 'Post Office Scheme'
  } else if (category === 'provident-funds') {
    amount = num(row.current_balance)
    label = str(row.type) ? `${str(row.type)}${row.account_number ? ` · ${str(row.account_number)}` : ''}` : 'Provident Fund'
  } else {
    amount = num(row.current_balance)
    label = str(row.account_number) || str(row.post_office_bank) || 'Sukanya Samriddhi'
  }

  const daysUntil = differenceInCalendarDays(parseISO(maturityDate), today)

  return {
    key: `${category}-${row.id}`,
    category,
    categoryLabel: CATEGORY_LABELS[category],
    label,
    profileId: typeof row.profile_id === 'number' ? row.profile_id : null,
    maturityDate,
    amount,
    isOverdue: daysUntil < 0,
    daysUntil,
  }
}

export function useMaturityAlerts() {
  const results = useQueries({
    queries: [
      { queryKey: ['assets', 'deposits', null], queryFn: () => depositsApi.list(null) },
      { queryKey: ['assets', 'provident-funds', null], queryFn: () => providentFundsApi.list(null) },
      { queryKey: ['assets', 'sukanya-samriddhi', null], queryFn: () => sukanyaApi.list(null) },
      { queryKey: ['assets', 'post-office', null], queryFn: () => postOfficeApi.list(null) },
    ],
  })

  const isLoading = results.some((r) => r.isLoading)
  const isError = results.some((r) => r.isError)

  const { upcoming, overdue } = useMemo(() => {
    const today = new Date()
    const categories: MaturityCategory[] = ['deposits', 'provident-funds', 'sukanya-samriddhi', 'post-office']
    const all: MaturityAlert[] = []

    results.forEach((result, idx) => {
      const rows = (result.data ?? []) as AssetRecord[]
      const category = categories[idx]
      rows.forEach((row) => {
        const alert = toAlert(row, category, today)
        if (alert) all.push(alert)
      })
    })

    const overdueAlerts = all.filter((a) => a.isOverdue).sort((a, b) => a.maturityDate.localeCompare(b.maturityDate))
    const upcomingAlerts = all
      .filter((a) => !a.isOverdue && a.daysUntil <= MATURITY_WINDOW_DAYS)
      .sort((a, b) => a.maturityDate.localeCompare(b.maturityDate))

    return { upcoming: upcomingAlerts, overdue: overdueAlerts }
  }, [results])

  return { upcoming, overdue, isLoading, isError }
}
