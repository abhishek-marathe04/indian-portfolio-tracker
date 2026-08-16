import { describe, expect, it } from 'vitest'
import { cn } from '../utils'

describe('cn', () => {
  it('joins plain class names', () => {
    expect(cn('a', 'b')).toBe('a b')
  })

  it('drops falsy values', () => {
    expect(cn('a', false, undefined, null, 'b')).toBe('a b')
  })

  it('merges conflicting Tailwind utility classes, keeping the last one', () => {
    expect(cn('px-2', 'px-4')).toBe('px-4')
  })

  it('supports the isActive-style conditional pattern used across the app', () => {
    const isActive = true
    expect(cn('base', isActive ? 'text-primary' : 'text-muted-foreground')).toBe('base text-primary')
  })
})
