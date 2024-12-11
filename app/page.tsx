'use client'

import { useState } from 'react'
import { SearchForm } from '@/components/search-form'
import { ThemeToggle } from '@/components/theme-toggle'
import { ChartComponent } from '@/components/chart'

export default function Home() {
  const [filters, setFilters] = useState({
    startDate: '',
    endDate: '',
    minAmount: '',
    maxAmount: '',
    description: '',
    category: '',
    account: ''
  })

  const handleSearch = (newFilters: any) => {
    setFilters(newFilters)
  }

  return (
    <main className="min-h-screen bg-background">
      <div className="container mx-auto p-4">
        <div className="flex justify-between items-center mb-4">
          <h1 className="text-2xl font-bold">Bank Transaction Dashboard</h1>
          <ThemeToggle />
        </div>
        <SearchForm onSearch={handleSearch} />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
          <ChartComponent filters={filters} chartType="bar" title="Bar Chart" />
          <ChartComponent filters={filters} chartType="donut" title="Pie Chart" />
          <ChartComponent filters={filters} chartType="area" title="Area Chart" />
          <ChartComponent filters={filters} chartType="line" title="Line Chart" />
        </div>
      </div>
    </main>
  )
}
