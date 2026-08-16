import { NavLink, Outlet, useSearchParams } from 'react-router-dom'
import { cn } from '../lib/utils'

const PORTFOLIO_NAV = [
  { path: 'mutual-funds', label: 'Mutual Funds' },
  { path: 'stocks', label: 'Stocks' },
  { path: 'deposits', label: 'Deposits' },
  { path: 'provident-funds', label: 'Provident Funds' },
  { path: 'sukanya-samriddhi', label: 'Sukanya Samriddhi' },
  { path: 'nps', label: 'NPS' },
  { path: 'gold', label: 'Gold' },
  { path: 'real-estate', label: 'Real Estate' },
  { path: 'international', label: 'International' },
  { path: 'crypto', label: 'Crypto' },
  { path: 'post-office', label: 'Post Office' },
  { path: 'savings-accounts', label: 'Savings Accounts' },
]

export default function PortfolioLayout() {
  const [searchParams] = useSearchParams()
  const search = searchParams.toString()

  return (
    <div>
      <nav className="mb-6 flex gap-1 overflow-x-auto no-scrollbar rounded-md bg-muted p-1">
        {PORTFOLIO_NAV.map((item) => (
          <NavLink
            key={item.path}
            to={`/portfolio/${item.path}${search ? `?${search}` : ''}`}
            className={({ isActive }) =>
              cn(
                'shrink-0 whitespace-nowrap rounded-sm px-3 py-2 text-sm font-medium transition-colors min-h-[2.25rem] flex items-center',
                isActive ? 'bg-background text-foreground shadow-sm' : 'text-muted-foreground hover:text-foreground',
              )
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
      <Outlet />
    </div>
  )
}
