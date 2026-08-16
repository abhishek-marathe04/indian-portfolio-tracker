import { apiClient } from './client'
import type { AuthUser } from '../types/api'

export async function login(username: string, password: string): Promise<void> {
  await apiClient.post('/auth/login', { username, password })
}

export async function logout(): Promise<void> {
  await apiClient.post('/auth/logout')
}

export async function fetchCurrentUser(): Promise<AuthUser> {
  const res = await apiClient.get<AuthUser>('/auth/me')
  return res.data
}

export async function changePassword(currentPassword: string, newPassword: string): Promise<void> {
  await apiClient.post('/auth/change-password', {
    current_password: currentPassword,
    new_password: newPassword,
  })
}
