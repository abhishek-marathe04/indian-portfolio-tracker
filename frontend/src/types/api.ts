export interface AuthUser {
  username: string
  created_at: string
}

export type Relationship = 'self' | 'spouse' | 'child' | 'parent' | 'other'

export interface Profile {
  id: number
  name: string
  relationship: Relationship
  date_of_birth?: string | null
  pan_number?: string | null
  created_at?: string
}

export interface ProfileInput {
  name: string
  relationship: Relationship
  date_of_birth?: string | null
  pan_number?: string | null
}

export interface NetWorthBreakdown {
  mutual_funds: number
  stocks: number
  deposits: number
  provident_fund: number
  sukanya_samriddhi: number
  nps: number
  gold: number
  real_estate: number
  international: number
  crypto: number
  post_office: number
  savings: number
}

export interface NetWorthSingle {
  profile_id: number
  total_value: number
  total_invested: number
  gain_loss: number
  gain_loss_pct: number
  breakdown: NetWorthBreakdown
}

export interface NetWorthConsolidated {
  consolidated: Omit<NetWorthSingle, 'profile_id'>
  per_profile: NetWorthSingle[]
}

export type NetWorthResponse = NetWorthSingle | NetWorthConsolidated

export function isConsolidatedNetWorth(r: NetWorthResponse): r is NetWorthConsolidated {
  return (r as NetWorthConsolidated).consolidated !== undefined
}

export interface AllocationResponse {
  total_value: number
  allocation: Record<string, number>
  // Omitted by the backend entirely when total_value is 0.
  breakdown_inr?: Record<string, number>
}

export interface CasUploadResult {
  status: string
  cas_type?: string
  investor_name?: string
  pan_detected?: string
  statement_date?: string | null
  folios_found?: number
  new_folios?: number
  updated_folios?: number
  new_transactions?: number
  equity_holdings_found?: number
  new_equity_holdings?: number
  nps_accounts_found?: number
  archived_as?: string
  message?: string
}

export interface BulkUploadResponse {
  job_id: string
  total_files: number
  message: string
}

export interface BulkFileStatus {
  filename: string
  status: 'queued' | 'processing' | 'done' | 'duplicate' | 'error'
  message?: string
  folios_found?: number
  new_transactions?: number
}

export interface BulkStatusResponse {
  status: 'running' | 'complete'
  total_files: number
  processed: number
  total_new_transactions: number
  files: BulkFileStatus[]
}

export interface ImportRecord {
  filename: string
  size_kb: number
  uploaded_at: string
}

export interface PortfolioValuePoint {
  month: string   // YYYY-MM-01
  total_value: number
}

export type XirrAssetType = 'all' | 'mutual_funds' | 'stocks'

export interface PerformanceResponse {
  value_over_time: PortfolioValuePoint[]
  xirr_pct: number | null
  xirr_asset_type: XirrAssetType
  xirr_note: string
}
