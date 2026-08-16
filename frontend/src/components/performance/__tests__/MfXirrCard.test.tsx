import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MfXirrCard } from '../MfXirrCard'

describe('MfXirrCard', () => {
  it('shows an explanatory message instead of a number when xirrPct is null', () => {
    render(<MfXirrCard xirrPct={null} note="scope note" />)
    expect(screen.getByText(/not enough transaction history/i)).toBeInTheDocument()
    expect(screen.queryByText('%')).not.toBeInTheDocument()
  })

  it('renders a positive XIRR with the gain styling', () => {
    render(<MfXirrCard xirrPct={12.34} note="scope note" />)
    expect(screen.getByText('12.34%')).toBeInTheDocument()
    expect(screen.getByText('12.34%').closest('div')).toHaveClass('text-gain')
  })

  it('renders a negative XIRR with the loss styling', () => {
    render(<MfXirrCard xirrPct={-8.5} note="scope note" />)
    expect(screen.getByText('-8.50%')).toBeInTheDocument()
    expect(screen.getByText('-8.50%').closest('div')).toHaveClass('text-loss')
  })

  it('renders the passed-through scope note', () => {
    render(<MfXirrCard xirrPct={5} note="mutual funds only" />)
    expect(screen.getByText('mutual funds only')).toBeInTheDocument()
  })
})
