import { describe, expect, it } from 'vitest'
import { formatDate, formatINR, formatNumber, formatPct } from '../formatters'

describe('formatINR', () => {
  it('formats with Indian lakh/crore grouping', () => {
    expect(formatINR(1234567)).toBe('₹12,34,567')
    expect(formatINR(100000)).toBe('₹1,00,000')
  })

  it('rounds to whole rupees by default', () => {
    expect(formatINR(1234.56)).toBe('₹1,235')
  })

  it('keeps 2 decimals when decimals=true', () => {
    expect(formatINR(1234.5, true)).toBe('₹1,234.50')
  })

  it('returns an em dash for null/undefined/NaN', () => {
    expect(formatINR(null)).toBe('—')
    expect(formatINR(undefined)).toBe('—')
    expect(formatINR(NaN)).toBe('—')
  })

  it('formats zero and negative values', () => {
    expect(formatINR(0)).toBe('₹0')
    expect(formatINR(-5000)).toBe('-₹5,000')
  })
})

describe('formatNumber', () => {
  it('formats with Indian grouping and default 2 decimals', () => {
    expect(formatNumber(123456.789)).toBe('1,23,456.79')
  })

  it('respects a custom decimals count', () => {
    expect(formatNumber(123.456, 0)).toBe('123')
  })

  it('returns an em dash for null/undefined/NaN', () => {
    expect(formatNumber(null)).toBe('—')
    expect(formatNumber(undefined)).toBe('—')
    expect(formatNumber(NaN)).toBe('—')
  })
})

describe('formatPct', () => {
  it('formats with a trailing % and default 2 decimals', () => {
    expect(formatPct(12.3456)).toBe('12.35%')
  })

  it('respects a custom decimals count', () => {
    expect(formatPct(12.3456, 1)).toBe('12.3%')
  })

  it('handles negative percentages', () => {
    expect(formatPct(-5.5)).toBe('-5.50%')
  })

  it('returns an em dash for null/undefined/NaN', () => {
    expect(formatPct(null)).toBe('—')
    expect(formatPct(undefined)).toBe('—')
    expect(formatPct(NaN)).toBe('—')
  })
})

describe('formatDate', () => {
  it('formats an ISO date string as "DD Mon YYYY"', () => {
    expect(formatDate('2026-07-31')).toBe('31 Jul 2026')
  })

  it('returns an em dash for null/undefined/empty', () => {
    expect(formatDate(null)).toBe('—')
    expect(formatDate(undefined)).toBe('—')
    expect(formatDate('')).toBe('—')
  })

  it('returns an em dash for an unparseable date', () => {
    expect(formatDate('not-a-date')).toBe('—')
  })
})
