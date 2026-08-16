import { apiClient } from './client'
import type { BulkStatusResponse, BulkUploadResponse, CasUploadResult, ImportRecord } from '../types/api'

export async function uploadCas(file: File, password: string, profileId: number): Promise<CasUploadResult> {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('password', password)
  formData.append('profile_id', String(profileId))
  const res = await apiClient.post<CasUploadResult>('/cas/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return res.data
}

export async function bulkUploadCas(
  files: File[],
  password: string,
  profileId: number,
): Promise<BulkUploadResponse> {
  const formData = new FormData()
  files.forEach((f) => formData.append('files', f))
  formData.append('password', password)
  formData.append('profile_id', String(profileId))
  const res = await apiClient.post<BulkUploadResponse>('/cas/bulk-upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return res.data
}

export async function fetchBulkStatus(jobId: string): Promise<BulkStatusResponse> {
  const res = await apiClient.get<BulkStatusResponse>(`/cas/bulk-status/${jobId}`)
  return res.data
}

export async function fetchImports(): Promise<ImportRecord[]> {
  const res = await apiClient.get<ImportRecord[]>('/cas/imports')
  return res.data
}
