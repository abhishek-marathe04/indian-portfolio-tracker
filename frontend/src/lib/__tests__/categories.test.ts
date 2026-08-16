import { describe, expect, it } from 'vitest'
import { categoryColor, categoryLabel, CATEGORY_COLORS, CATEGORY_LABELS } from '../categories'

describe('categoryLabel', () => {
  it('returns the friendly label for a known category', () => {
    expect(categoryLabel('mutual_funds')).toBe('Mutual Funds')
    expect(categoryLabel('nps')).toBe('NPS')
  })

  it('falls back to the raw key for an unknown category', () => {
    expect(categoryLabel('some_new_asset_class')).toBe('some_new_asset_class')
  })
})

describe('categoryColor', () => {
  it('returns the fixed color for a known category', () => {
    expect(categoryColor('mutual_funds')).toBe('#2563eb')
  })

  it('falls back to a neutral gray for an unknown category', () => {
    expect(categoryColor('some_new_asset_class')).toBe('#64748b')
  })
})

describe('category maps', () => {
  it('define a color for every labeled category (no silent gray fallback in the UI)', () => {
    for (const key of Object.keys(CATEGORY_LABELS)) {
      expect(CATEGORY_COLORS[key], `missing color for "${key}"`).toBeDefined()
    }
  })
})
