import type { ReactNode } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQueryClient } from '@tanstack/react-query'
import { LogOut } from 'lucide-react'
import { Sidebar } from './Sidebar'
import { BottomTabBar } from './BottomTabBar'
import { ProfileSwitcher } from './ProfileSwitcher'
import { Button } from '../ui/button'
import { Toaster } from '../ui/toaster'
import { logout } from '../../api/auth'
import { useToast } from '../ui/use-toast'

export function AppShell({ children }: { children: ReactNode }) {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { toast } = useToast()

  async function handleLogout() {
    try {
      await logout()
    } catch {
      // ignore — we're navigating away regardless
    }
    queryClient.clear()
    navigate('/login', { replace: true })
  }

  async function handleLogoutClick() {
    try {
      await handleLogout()
    } catch (err) {
      toast({ variant: 'destructive', title: 'Logout failed', description: String(err) })
    }
  }

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      <div className="flex flex-1 flex-col">
        <header className="sticky top-0 z-30 flex h-16 items-center justify-between gap-3 border-b border-border bg-card/95 px-4 backdrop-blur sm:px-6">
          <div className="min-w-0 flex-1">
            <ProfileSwitcher />
          </div>
          <Button variant="ghost" size="icon" onClick={handleLogoutClick} aria-label="Log out">
            <LogOut className="h-5 w-5" />
          </Button>
        </header>
        <main className="flex-1 px-4 pb-24 pt-6 sm:px-6 md:pb-6">{children}</main>
      </div>
      <BottomTabBar />
      <Toaster />
    </div>
  )
}
