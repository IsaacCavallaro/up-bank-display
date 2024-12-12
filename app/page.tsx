'use client'

import { useState } from 'react'
import { SearchForm } from '@/components/search-form'
import { ThemeToggle } from '@/components/theme-toggle'
import { ChartComponent } from '@/components/chart'

export default function Home() {
  const [currentView, setCurrentView] = useState<'home' | 'search'>('home') // Tracks the current view
  const [filters, setFilters] = useState({
    startDate: '',
    endDate: '',
    minAmount: '',
    maxAmount: '',
    description: '',
    category: '',
    account: '',
  })

  const handleSearch = (newFilters: any) => {
    setFilters(newFilters)
    setCurrentView('search') // Switch to search view on search
  }

  return (
    <main className="min-h-screen bg-background">
      <div className="container mx-auto p-4">
        <div className="flex justify-between items-center mb-4">
          <h1 className="text-2xl font-bold">Bank Transaction Dashboard</h1>
          <ThemeToggle />
        </div>
        <nav className="flex justify-start space-x-4 mb-6">
          <button
            className={`px-4 py-2 rounded ${currentView === 'home' ? 'bg-primary text-white' : 'bg-secondary text-primary'
              }`}
            onClick={() => setCurrentView('home')}
          >
            Home
          </button>
          <button
            className={`px-4 py-2 rounded ${currentView === 'search' ? 'bg-primary text-white' : 'bg-secondary text-primary'
              }`}
            onClick={() => setCurrentView('search')}
          >
            Search
          </button>
        </nav>

        {currentView === 'home' ? (
          // Home View: Display all accounts data
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <ChartComponent
              filters={{ account: 'ALL', startDate: '', endDate: '' }}
              chartType="bar"
              title="All Accounts Bar Chart (Last 4 Weeks)"
            />
            <ChartComponent
              filters={{ account: 'ALL', startDate: '', endDate: '' }}
              chartType="donut"
              title="All Accounts Pie Chart (Last 4 Weeks)"
            />
            <ChartComponent
              filters={{ account: 'ALL', startDate: '', endDate: '' }}
              chartType="area"
              title="All Accounts Area Chart (Last 4 Weeks)"
            />
            <ChartComponent
              filters={{ account: 'ALL', startDate: '', endDate: '' }}
              chartType="line"
              title="All Accounts Line Chart (Last 4 Weeks)"
            />
          </div>
        ) : (
          // Search View: Display charts based on search filters
          <>
            <SearchForm onSearch={handleSearch} />
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
              <ChartComponent filters={filters} chartType="bar" title="Bar Chart" />
              <ChartComponent filters={filters} chartType="donut" title="Pie Chart" />
              <ChartComponent filters={filters} chartType="area" title="Area Chart" />
              <ChartComponent filters={filters} chartType="line" title="Line Chart" />
            </div>
          </>
        )}
      </div>
    </main>
  )
}
