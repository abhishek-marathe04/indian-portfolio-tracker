/**
 * Fixed category -> label/color map for the 12 net-worth/allocation categories.
 * Defined once so colors stay stable across profile switches (not Recharts' auto-palette).
 */
export const CATEGORY_LABELS: Record<string, string> = {
  mutual_funds: 'Mutual Funds',
  stocks: 'Stocks',
  deposits: 'Deposits (FD/RD)',
  provident_fund: 'Provident Fund',
  sukanya_samriddhi: 'Sukanya Samriddhi',
  nps: 'NPS',
  gold: 'Gold',
  real_estate: 'Real Estate',
  international: 'International',
  crypto: 'Crypto',
  post_office: 'Post Office',
  savings: 'Savings Accounts',
}

export const CATEGORY_COLORS: Record<string, string> = {
  mutual_funds: '#2563eb',
  stocks: '#7c3aed',
  deposits: '#059669',
  provident_fund: '#d97706',
  sukanya_samriddhi: '#db2777',
  nps: '#0891b2',
  gold: '#ca8a04',
  real_estate: '#4338ca',
  international: '#16a34a',
  crypto: '#dc2626',
  post_office: '#9333ea',
  savings: '#0d9488',
}

export function categoryLabel(key: string): string {
  return CATEGORY_LABELS[key] ?? key
}

export function categoryColor(key: string): string {
  return CATEGORY_COLORS[key] ?? '#64748b'
}
