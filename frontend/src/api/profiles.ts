import { apiClient } from './client'
import type { Profile, ProfileInput } from '../types/api'

export async function listProfiles(): Promise<Profile[]> {
  const res = await apiClient.get<Profile[]>('/profiles')
  return res.data
}

export async function createProfile(data: ProfileInput): Promise<Profile> {
  const res = await apiClient.post<Profile>('/profiles', data)
  return res.data
}

export async function updateProfile(id: number, data: Partial<ProfileInput>): Promise<Profile> {
  const res = await apiClient.put<Profile>(`/profiles/${id}`, data)
  return res.data
}

export async function deleteProfile(id: number): Promise<void> {
  await apiClient.delete(`/profiles/${id}`)
}
