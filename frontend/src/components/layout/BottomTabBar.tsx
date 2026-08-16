import { NavLink } from 'react-router-dom'
import { cn } from '../../lib/utils'
import { NAV_ITEMS } from './navItems'

export function BottomTabBar() {
  return (
    <nav className="fixed inset-x-0 bottom-0 z-40 flex border-t border-border bg-card md:hidden overflow-x-auto no-scrollbar">
      {NAV_ITEMS.map((item) => (
        <NavLink
          key={item.path}
          to={item.path}
          end={item.path === '/'}
          className={({ isActive }) =>
            cn(
              'flex min-w-[64px] flex-1 flex-col items-center justify-center gap-1 py-2 text-[11px] font-medium min-h-[56px]',
              isActive ? 'text-primary' : 'text-muted-foreground',
            )
          }
        >
          <item.icon className="h-5 w-5" />
          <span className="leading-none">{item.label.split(' ')[0]}</span>
        </NavLink>
      ))}
    </nav>
  )
}
