'use client'

import { useState, useEffect } from 'react'
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  PieChart,
  Pie,
  AreaChart,
  Area,
  LineChart,
  Line,
  Tooltip,
  Legend,
  Cell
} from 'recharts'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'

interface Transaction {
  id: string
  attributes: {
    amount: { value: string }
    category: string
    description: string
    createdAt: string
  }
}

type ChartType = 'bar' | 'donut' | 'area' | 'line'

interface ChartComponentProps {
  filters: any
  chartType: ChartType
  title: string
}

export function ChartComponent({ filters, chartType, title }: ChartComponentProps) {
  const [data, setData] = useState<Transaction[]>([])
  const [loading, setLoading] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      setError(null)
      try {
        const response = await fetch('/api/search', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(filters),
        })

        if (!response.ok) throw new Error('Failed to fetch data')

        const result = await response.json()
        setData(result.data || [])
      } catch (error: any) {
        setError('Error fetching data: ' + error.message)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [filters])

  const totalWithdrawals = data
    .filter(transaction => parseFloat(transaction.attributes.amount.value) < 0)
    .reduce((acc, transaction) => acc + parseFloat(transaction.attributes.amount.value), 0)

  const totalDeposits = data
    .filter(transaction => parseFloat(transaction.attributes.amount.value) >= 0)
    .reduce((acc, transaction) => acc + parseFloat(transaction.attributes.amount.value), 0)

  const colors = ['#8884d8', '#82ca9d', '#ffc658', '#ff8042']

  const renderChart = () => {
    switch (chartType) {
      case 'bar':
        return (
          <BarChart data={data}>
            <XAxis dataKey="attributes.category" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="attributes.amount.value" fill="#8884d8">
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
              ))}
            </Bar>
          </BarChart>
        )
      case 'donut':
        const totalAmount = data.reduce(
          (acc, transaction) => acc + parseFloat(transaction.attributes.amount.value),
          0
        )
        const donutData = data.map(transaction => ({
          name: transaction.attributes.category,
          value: Math.abs(parseFloat(transaction.attributes.amount.value)),
        }))
        return (
          <PieChart>
            <Pie
              data={donutData}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={80}
              paddingAngle={5}
              dataKey="value"
              label={({ value, percent }) =>
                `$${value.toFixed(0)} (${(percent * 100).toFixed(1)}%)`
              }
              labelLine={false}
            >
              {donutData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
              ))}
            </Pie>
            <Tooltip />
            <text
              x="50%"
              y="50%"
              textAnchor="middle"
              dominantBaseline="middle"
              style={{
                fontSize: '24px',
                fontWeight: 'bold',
                fill: 'currentColor',
              }}
            >
              {`$${(totalAmount / 1000).toFixed(1)}K`}
            </text>
            <text
              x="50%"
              y="58%"
              textAnchor="middle"
              dominantBaseline="middle"
              style={{
                fontSize: '14px',
                fill: 'currentColor',
              }}
            >
              Total Amount
            </text>
          </PieChart>
        )
      case 'area':
        return (
          <AreaChart data={data}>
            <XAxis dataKey="attributes.createdAt" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Area type="monotone" dataKey="attributes.amount.value" stroke="#8884d8" fill="#8884d8" />
          </AreaChart>
        )
      case 'line':
        return (
          <LineChart data={data}>
            <XAxis dataKey="attributes.createdAt" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="attributes.amount.value" stroke="#8884d8" />
          </LineChart>
        )
      default:
        return null
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent>
        {loading && <div>Loading...</div>}
        {error && <div className="text-red-500">{error}</div>}
        <div style={{ width: '100%', height: '300px' }}>
          <ResponsiveContainer>
            {renderChart()}
          </ResponsiveContainer>
        </div>
        <div className="mt-2">
          <div>Total Withdrawals: ${totalWithdrawals.toFixed(2)}</div>
          <div>Total Deposits: ${totalDeposits.toFixed(2)}</div>
        </div>
      </CardContent>
    </Card>
  )
}
