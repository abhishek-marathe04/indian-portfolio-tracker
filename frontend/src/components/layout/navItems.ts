import type { LucideIcon } from 'lucide-react'
import { LayoutDashboard, LineChart, Wallet, Target, BellRing, Upload, Users, Settings } from 'lucide-react'

export interface NavItem {
  label: string
  path: string
  icon: LucideIcon
}

export const NAV_ITEMS: NavItem[] = [
  { label: 'Dashboard', path: '/', icon: LayoutDashboard },
  { label: 'Performance', path: '/performance', icon: LineChart },
  { label: 'Portfolio', path: '/portfolio', icon: Wallet },
  { label: 'Goals', path: '/goals', icon: Target },
  { label: 'Maturity Alerts', path: '/maturity-alerts', icon: BellRing },
  { label: 'Upload CAS', path: '/upload-cas', icon: Upload },
  { label: 'Family Profiles', path: '/family-profiles', icon: Users },
  { label: 'Settings', path: '/settings', icon: Settings },
]
