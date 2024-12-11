'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'

const ACCOUNT_IDS = {
  IC_INDIVIDUAL: process.env.IC_INDIVIDUAL || '',
  TWO_UP: process.env.TWO_UP || '',
  BILLS: process.env.BILLS || '',
  GIFTS: process.env.GIFTS || '',
  KIDS: process.env.KIDS || '',
  EXTRAS: process.env.EXTRAS || '',
  HOLIDAYS: process.env.HOLIDAYS || '',
  SUPER: process.env.SUPER || '',
  INVESTMENTS: process.env.INVESTMENTS || '',
  RAINY_DAY: process.env.RAINY_DAY || '',
  EMERGENCY: process.env.EMERGENCY || '',
  HOME_DEPOSIT: process.env.HOME_DEPOSIT || '',
  TRANSPORT: process.env.TRANSPORT || '',
  HEALTH: process.env.HEALTH || '',
  GROCERIES: process.env.GROCERIES || '',
  PERSONAL_SAVER: process.env.PERSONAL_SAVER || '',
  RENT: process.env.RENT || '',
}

const CATEGORIES = ["personal", "good-life", "home", "transport"]

export function SearchForm({ onSearch }: { onSearch: (filters: any) => void }) {
  const [filters, setFilters] = useState({
    startDate: '',
    endDate: '',
    minAmount: '',
    maxAmount: '',
    description: '',
    category: '',
    account: '',
  })

  const [allAccounts, setAllAccounts] = useState(false) // State for the "All Accounts" checkbox

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    const accountId = allAccounts ? 'ALL' : ACCOUNT_IDS[filters.account] || filters.account

    const filtersWithDates = {
      ...filters,
      account: accountId, // Send 'ALL' if the checkbox is checked, or the selected account key
    }

    const sanitizedFilters = Object.fromEntries(
      Object.entries(filtersWithDates).filter(([_, value]) => value !== '' && value !== undefined)
    )

    onSearch(sanitizedFilters)
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFilters(prev => ({ ...prev, [name]: value }))
  }

  const handleSelectChange = (name: string, value: string) => {
    setFilters(prev => ({ ...prev, [name]: value }))
  }

  const handleCheckboxChange = () => {
    setAllAccounts(prev => !prev)
    setFilters(prev => ({ ...prev, account: '' })) // Reset the account field when "All Accounts" is selected
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <Label htmlFor="startDate">Start Date</Label>
          <Input
            id="startDate"
            name="startDate"
            type="date"
            value={filters.startDate}
            onChange={handleInputChange}
          />
        </div>
        <div>
          <Label htmlFor="endDate">End Date</Label>
          <Input
            id="endDate"
            name="endDate"
            type="date"
            value={filters.endDate}
            onChange={handleInputChange}
          />
        </div>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <Label htmlFor="minAmount">Min Amount</Label>
          <Input
            id="minAmount"
            name="minAmount"
            type="number"
            value={filters.minAmount}
            onChange={handleInputChange}
          />
        </div>
        <div>
          <Label htmlFor="maxAmount">Max Amount</Label>
          <Input
            id="maxAmount"
            name="maxAmount"
            type="number"
            value={filters.maxAmount}
            onChange={handleInputChange}
          />
        </div>
      </div>
      <div>
        <Label htmlFor="description">Description</Label>
        <Input
          id="description"
          name="description"
          type="text"
          value={filters.description}
          onChange={handleInputChange}
        />
      </div>

      {/* Category Select */}
      <div>
        <Label htmlFor="category">Category</Label>
        <Select value={filters.category} onValueChange={(value) => handleSelectChange('category', value)}>
          <SelectTrigger>
            <SelectValue placeholder="Select Category" />
          </SelectTrigger>
          <SelectContent>
            {CATEGORIES.map((category) => (
              <SelectItem key={category} value={category}>
                {category}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Account Select */}
      <div>
        <Label htmlFor="account">Account</Label>
        <Select
          value={filters.account}
          onValueChange={(value) => handleSelectChange('account', value)}
          disabled={allAccounts} // Disable select if "All Accounts" is checked
        >
          <SelectTrigger>
            <SelectValue placeholder="Select Account" />
          </SelectTrigger>
          <SelectContent>
            {Object.keys(ACCOUNT_IDS).map((accountKey) => (
              <SelectItem key={accountKey} value={accountKey}>
                {accountKey}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* All Accounts Checkbox */}
      <div>
        <Label>
          <input
            type="checkbox"
            checked={allAccounts}
            onChange={handleCheckboxChange}
            className="mr-2"
          />
          All Accounts
        </Label>
      </div>

      <Button type="submit">Apply Filters</Button>
    </form>
  )
}
