import { apiClient } from './client'
import type { AssetApi, AssetRecord } from '../types/asset'

export function makeAssetApi<T extends AssetRecord = AssetRecord>(resourcePath: string): AssetApi<T> {
  return {
    async list(profileId) {
      const params = profileId !== null && profileId !== undefined ? { profile_id: profileId } : {}
      const res = await apiClient.get<T[]>(`/assets/${resourcePath}`, { params })
      return res.data
    },
    async create(data) {
      const res = await apiClient.post<T>(`/assets/${resourcePath}`, data)
      return res.data
    },
    async update(id, data) {
      const res = await apiClient.put<T>(`/assets/${resourcePath}/${id}`, data)
      return res.data
    },
    async remove(id) {
      await apiClient.delete(`/assets/${resourcePath}/${id}`)
    },
  }
}
