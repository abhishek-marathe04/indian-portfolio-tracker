import { apiClient } from './client'
import type { AllocationResponse, NetWorthResponse, PerformanceResponse, XirrAssetType } from '../types/api'

export async function fetchNetWorth(profileId?: number | null): Promise<NetWorthResponse> {
  const params = profileId !== null && profileId !== undefined ? { profile_id: profileId } : {}
  const res = await apiClient.get<NetWorthResponse>('/analytics/net-worth', { params })
  return res.data
}

export async function fetchAllocation(profileId?: number | null): Promise<AllocationResponse> {
  const params = profileId !== null && profileId !== undefined ? { profile_id: profileId } : {}
  const res = await apiClient.get<AllocationResponse>('/analytics/allocation', { params })
  return res.data
}

export async function refreshPrices(): Promise<{ message: string }> {
  const res = await apiClient.post<{ message: string }>('/analytics/refresh-prices')
  return res.data
}

export async function fetchPerformance(
  profileId?: number | null,
  assetType: XirrAssetType = 'all',
  folioNumber?: string | null,
): Promise<PerformanceResponse> {
  const params: Record<string, unknown> = { asset_type: assetType }
  if (profileId !== null && profileId !== undefined) params.profile_id = profileId
  if (assetType === 'mutual_funds' && folioNumber) params.folio_number = folioNumber
  const res = await apiClient.get<PerformanceResponse>('/analytics/performance', { params })
  return res.data
}
