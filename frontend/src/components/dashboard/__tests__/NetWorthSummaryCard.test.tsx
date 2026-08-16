import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'
import { NetWorthSummaryCard } from '../NetWorthSummaryCard'

describe('NetWorthSummaryCard', () => {
  it('renders the total value and a gain in the gain color', () => {
    render(<NetWorthSummaryCard totalValue={3535126} gainLoss={500000} gainLossPct={16.5} />)
    expect(screen.getByText('₹35,35,126')).toBeInTheDocument()
    const gainLine = screen.getByText(/₹5,00,000/).closest('div')
    expect(gainLine).toHaveClass('text-gain')
    expect(gainLine).toHaveTextContent('16.50%')
  })

  it('renders a loss in the loss color using the absolute value', () => {
    render(<NetWorthSummaryCard totalValue={2000000} gainLoss={-150000} gainLossPct={-7.2} />)
    const lossLine = screen.getByText(/₹1,50,000/).closest('div')
    expect(lossLine).toHaveClass('text-loss')
    expect(lossLine).toHaveTextContent('7.20%')
    expect(lossLine).not.toHaveTextContent('-₹')
  })

  it('treats exactly zero gain/loss as a gain (>= 0)', () => {
    render(<NetWorthSummaryCard totalValue={1000000} gainLoss={0} gainLossPct={0} />)
    expect(screen.getByText(/₹0/).closest('div')).toHaveClass('text-gain')
  })
})
