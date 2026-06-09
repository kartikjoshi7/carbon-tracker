/**
 * Frontend smoke tests and automated accessibility (axe) assertions.
 *
 * These tests validate that:
 * 1. Core components render without crashing
 * 2. Key interactive elements are present in the DOM
 * 3. The rendered HTML has ZERO accessibility violations (via axe-core)
 */
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { configureAxe, toHaveNoViolations } from 'jest-axe'
import App from '../App'

// Extend vitest matchers with axe accessibility assertions
expect.extend(toHaveNoViolations)

const axe = configureAxe({
  rules: {
    // Disable color-contrast in jsdom (it can't compute styles)
    'color-contrast': { enabled: false },
  },
})

describe('App — Smoke Tests', () => {
  it('renders the hero title', () => {
    render(<App />)
    expect(screen.getByText('Carbon Footprint Awareness Platform')).toBeInTheDocument()
  })

  it('renders the hero subtitle', () => {
    render(<App />)
    expect(screen.getByText(/Real-time CO.*tracking/)).toBeInTheDocument()
  })

  it('renders tab navigation with 3 tabs', () => {
    render(<App />)
    expect(screen.getByText('Track Footprint')).toBeInTheDocument()
    expect(screen.getByText('Data Analytics')).toBeInTheDocument()
    expect(screen.getByText('Leaderboard')).toBeInTheDocument()
  })

  it('renders all 3 tracking forms on the Track tab', () => {
    render(<App />)
    expect(screen.getByText('Energy Tracking')).toBeInTheDocument()
    expect(screen.getByText('Transit Tracking')).toBeInTheDocument()
    expect(screen.getByText('Waste Tracking')).toBeInTheDocument()
  })

  it('renders the AI Receipt Parsing section', () => {
    render(<App />)
    expect(screen.getByText(/AI Receipt Parsing/)).toBeInTheDocument()
  })

  it('renders the AI Eco-Concierge panel', () => {
    render(<App />)
    expect(screen.getByText('AI Eco-Concierge Insights')).toBeInTheDocument()
  })
})

describe('App — Accessibility (axe-core)', () => {
  it('has zero accessibility violations on the Track tab', async () => {
    const { container } = render(<App />)
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})

describe('Form Labels — Accessibility', () => {
  it('all energy form inputs have associated labels', () => {
    render(<App />)
    expect(screen.getByLabelText('Roommates Count')).toBeInTheDocument()
    expect(screen.getByLabelText('AC Hours Logged')).toBeInTheDocument()
    expect(screen.getByLabelText('Shared Appliance (kWh)')).toBeInTheDocument()
  })

  it('all transit form inputs have associated labels', () => {
    render(<App />)
    expect(screen.getByLabelText('Distance (km)')).toBeInTheDocument()
    expect(screen.getByLabelText('Transport Mode')).toBeInTheDocument()
    expect(screen.getByLabelText('Passenger Count')).toBeInTheDocument()
  })

  it('all waste form inputs have associated labels', () => {
    render(<App />)
    expect(screen.getByLabelText('Meal Type')).toBeInTheDocument()
    expect(screen.getByLabelText('Estimated Waste (grams)')).toBeInTheDocument()
  })

  it('tab navigation has proper ARIA roles', () => {
    render(<App />)
    const tablist = screen.getByRole('tablist')
    expect(tablist).toBeInTheDocument()
    const tabs = screen.getAllByRole('tab')
    expect(tabs.length).toBe(3)
  })
})
