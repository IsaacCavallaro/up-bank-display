'use client'

import { useState } from 'react'
import { SearchForm } from '@/components/search-form'
import { ChartComponent } from '@/components/chart'
import { ThemeToggle } from '@/components/theme-toggle'

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
          <h1 className="text-2xl font-bold">Bank Transaction Search</h1>
          <ThemeToggle />
        </div>
        <SearchForm onSearch={handleSearch} />
        <ChartComponent filters={filters} />
      </div>
    </main>
  )
}

