import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'
import { PortfolioValueChart } from '../PortfolioValueChart'

describe('PortfolioValueChart', () => {
  it('shows the empty-state hint when there is no history yet', () => {
    render(<PortfolioValueChart data={[]} />)
    expect(screen.getByText(/no history yet/i)).toBeInTheDocument()
  })

  it('renders the chart title and hides the empty-state hint once data is present', () => {
    render(
      <PortfolioValueChart
        data={[
          { month: '2025-08-01', total_value: 2207988.59 },
          { month: '2026-07-01', total_value: 3535126.28 },
        ]}
      />,
    )
    expect(screen.getByText('Portfolio Value Over Time')).toBeInTheDocument()
    expect(screen.queryByText(/no history yet/i)).not.toBeInTheDocument()
  })
})
