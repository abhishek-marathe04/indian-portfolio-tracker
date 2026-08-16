import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'
import { XirrCard } from '../XirrCard'

describe('XirrCard', () => {
  it('shows an explanatory message instead of a number when xirrPct is null', () => {
    render(<XirrCard xirrPct={null} note="scope note" assetType="all" />)
    expect(screen.getByText(/not enough transaction history/i)).toBeInTheDocument()
    expect(screen.queryByText('%')).not.toBeInTheDocument()
  })

  it('renders a positive XIRR with the gain styling', () => {
    render(<XirrCard xirrPct={12.34} note="scope note" assetType="all" />)
    expect(screen.getByText('12.34%')).toBeInTheDocument()
    expect(screen.getByText('12.34%').closest('div')).toHaveClass('text-gain')
  })

  it('renders a negative XIRR with the loss styling', () => {
    render(<XirrCard xirrPct={-8.5} note="scope note" assetType="all" />)
    expect(screen.getByText('-8.50%')).toBeInTheDocument()
    expect(screen.getByText('-8.50%').closest('div')).toHaveClass('text-loss')
  })

  it('renders the passed-through scope note', () => {
    render(<XirrCard xirrPct={5} note="mutual funds only" assetType="mutual_funds" />)
    expect(screen.getByText('mutual funds only')).toBeInTheDocument()
  })

  it('titles the card per asset type', () => {
    const { rerender } = render(<XirrCard xirrPct={5} note="n" assetType="mutual_funds" />)
    expect(screen.getByText('Mutual Fund XIRR')).toBeInTheDocument()

    rerender(<XirrCard xirrPct={5} note="n" assetType="stocks" />)
    expect(screen.getByText('Stock XIRR')).toBeInTheDocument()

    rerender(<XirrCard xirrPct={5} note="n" assetType="all" />)
    expect(screen.getByText('XIRR')).toBeInTheDocument()
  })
})
