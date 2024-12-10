'use client'

import { useState, useEffect } from 'react'
import { LineChart, Line, BarChart, Bar, AreaChart, Area, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'

type Transaction = {
  id: string
  attributes: {
    description: string
    amount: {
      currencyCode: string
      value: string
      valueInBaseUnits: number
    }
    settledAt: string
    category: string | null
    account: string
    status: string
    message: string
    transactionType: string
    performingCustomer: {
      displayName: string
    }
  }
  relationships: {
    category: { data: { id: string } | null }
  }
}

type TransactionData = {
  data: Transaction[]
}

type ChartType = 'line' | 'bar' | 'area' | 'donut'

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8']

export function ChartComponent({ filters }: { filters: any }) {
  const [data, setData] = useState<Transaction[]>([])
  const [chartType, setChartType] = useState<ChartType>('line')
  const [loading, setLoading] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      setError(null)  // Reset error state
      try {
        const response = await fetch('/api/search', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(filters),
        })

        if (!response.ok) {
          throw new Error('Failed to fetch data')
        }

        const result: TransactionData = await response.json()
        setData(result.data || [])
      } catch (error) {
        setError('Error fetching data: ' + error.message)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [filters])

  const amount = data.length > 0 ? parseFloat(data[0].attributes.amount.value) : null

  const renderChart = () => {
    const CommonProps = {
      data: data.map(transaction => ({
        date: new Date(transaction.attributes.settledAt).toLocaleDateString(),
        amount: parseFloat(transaction.attributes.amount.value),
        category: transaction.relationships.category?.data?.id || 'Unknown',
      })),
      margin: { top: 10, right: 30, left: 0, bottom: 0 },
    }

    switch (chartType) {
      case 'bar':
        return (
          <BarChart {...CommonProps}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip
              formatter={(value) => [`$${Math.abs(value).toFixed(2)}`, 'Amount']}
              labelFormatter={(label) => `Date: ${label}`}
            />
            <Legend />
            <Bar dataKey="amount" name="Transaction Amount" fill="#8884d8" />
          </BarChart>
        )
      case 'area':
        return (
          <AreaChart {...CommonProps}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip
              formatter={(value) => [`$${Math.abs(value).toFixed(2)}`, 'Amount']}
              labelFormatter={(label) => `Date: ${label}`}
            />
            <Legend />
            <Area type="monotone" dataKey="amount" name="Transaction Amount" stroke="#8884d8" fill="#8884d8" />
          </AreaChart>
        )
      case 'donut':
        return (
          <PieChart>
            <Pie
              data={data.map(transaction => ({
                name: transaction.relationships.category?.data?.id || 'Unknown',
                value: Math.abs(parseFloat(transaction.attributes.amount.value)),
              }))}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={80}
              fill="#8884d8"
              paddingAngle={5}
              dataKey="value"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip formatter={(value) => `$${value.toFixed(2)}`} />
            <Legend />
          </PieChart>
        )
      default:
        return (
          <LineChart {...CommonProps}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip
              formatter={(value) => [`$${Math.abs(value).toFixed(2)}`, 'Amount']}
              labelFormatter={(label) => `Date: ${label}`}
            />
            <Legend />
            <Line type="monotone" dataKey="amount" name="Transaction Amount" stroke="#8884d8" activeDot={{ r: 8 }} />
          </LineChart>
        )
    }
  }

  return (
    <Card className="mt-8">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle>Transaction History</CardTitle>
        <Select value={chartType} onValueChange={(value: ChartType) => setChartType(value)}>
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Select chart type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="line">Line Chart</SelectItem>
            <SelectItem value="bar">Bar Chart</SelectItem>
            <SelectItem value="area">Area Chart</SelectItem>
            <SelectItem value="donut">Donut Chart</SelectItem>
          </SelectContent>
        </Select>
      </CardHeader>
      <CardContent>
        {loading && <div>Loading...</div>}
        {error && <div className="text-red-500">{error}</div>}
        {amount !== null && (
          <div className="text-xl font-semibold">
            Amount: ${amount.toFixed(2)}
          </div>
        )}
        <ResponsiveContainer width="100%" height={400}>
          {renderChart()}
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}
