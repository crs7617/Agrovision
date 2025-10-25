'use client'

import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { 
  Search, 
  Download, 
  TrendingUp, 
  TrendingDown, 
  Activity,
  Calendar
} from 'lucide-react'
import { useState } from 'react'
import { formatDistanceToNow } from 'date-fns'
import Link from 'next/link'

// Mock analysis data
const mockAnalyses = [
  {
    id: '1',
    farm_name: 'Green Valley Farm',
    farm_id: '1',
    date: new Date('2025-02-10'),
    health_score: 85,
    previous_score: 78,
    ndvi: 0.75,
    evi: 0.55,
    savi: 0.65,
    status: 'completed',
    findings: 'Excellent vegetation health with uniform growth patterns',
  },
  {
    id: '2',
    farm_name: 'Sunset Acres',
    farm_id: '2',
    date: new Date('2025-02-09'),
    health_score: 72,
    previous_score: 75,
    ndvi: 0.68,
    evi: 0.48,
    savi: 0.58,
    status: 'completed',
    findings: 'Slight decrease in health, potential water stress detected',
  },
  {
    id: '3',
    farm_name: 'North Field',
    farm_id: '3',
    date: new Date('2025-02-08'),
    health_score: 92,
    previous_score: 90,
    ndvi: 0.82,
    evi: 0.62,
    savi: 0.72,
    status: 'completed',
    findings: 'Optimal crop health with strong vegetation indices',
  },
]

export default function AnalysisPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')

  const getHealthColor = (score: number) => {
    if (score >= 80) return 'text-emerald-500'
    if (score >= 60) return 'text-yellow-500'
    return 'text-red-500'
  }

  const getStatusBadge = (status: string) => {
    const colors = {
      completed: 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20',
      'in-progress': 'bg-blue-500/10 text-blue-500 border-blue-500/20',
      failed: 'bg-red-500/10 text-red-500 border-red-500/20',
    }
    return colors[status as keyof typeof colors] || colors.completed
  }

  const filteredAnalyses = mockAnalyses.filter((analysis) => {
    const matchesSearch = analysis.farm_name.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesStatus = statusFilter === 'all' || analysis.status === statusFilter
    return matchesSearch && matchesStatus
  })

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Analysis History</h1>
          <p className="text-gray-400">
            View and compare all crop health analyses
          </p>
        </div>
        <Button className="bg-emerald-600 hover:bg-emerald-700 text-white">
          <Download className="mr-2 h-4 w-4" />
          Export All
        </Button>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
          <Input
            placeholder="Search by farm name..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10 bg-zinc-900 border-white/20 text-white placeholder:text-gray-500"
          />
        </div>
        <div className="flex gap-2">
          <Button
            variant={statusFilter === 'all' ? 'default' : 'outline'}
            onClick={() => setStatusFilter('all')}
            className={statusFilter === 'all' ? 'bg-emerald-600 hover:bg-emerald-700' : 'border-white/20 text-white hover:bg-white/5'}
          >
            All
          </Button>
          <Button
            variant={statusFilter === 'completed' ? 'default' : 'outline'}
            onClick={() => setStatusFilter('completed')}
            className={statusFilter === 'completed' ? 'bg-emerald-600 hover:bg-emerald-700' : 'border-white/20 text-white hover:bg-white/5'}
          >
            Completed
          </Button>
          <Button
            variant={statusFilter === 'in-progress' ? 'default' : 'outline'}
            onClick={() => setStatusFilter('in-progress')}
            className={statusFilter === 'in-progress' ? 'bg-emerald-600 hover:bg-emerald-700' : 'border-white/20 text-white hover:bg-white/5'}
          >
            In Progress
          </Button>
        </div>
      </div>

      {/* Analysis Table */}
      <Card className="bg-zinc-900 border-white/10 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="border-b border-white/10">
              <tr className="text-left">
                <th className="p-4 text-sm font-medium text-gray-400">Farm</th>
                <th className="p-4 text-sm font-medium text-gray-400">Date</th>
                <th className="p-4 text-sm font-medium text-gray-400">Health Score</th>
                <th className="p-4 text-sm font-medium text-gray-400">Change</th>
                <th className="p-4 text-sm font-medium text-gray-400">Key Findings</th>
                <th className="p-4 text-sm font-medium text-gray-400">Status</th>
                <th className="p-4 text-sm font-medium text-gray-400">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/10">
              {filteredAnalyses.map((analysis) => {
                const scoreChange = analysis.health_score - analysis.previous_score
                const isPositive = scoreChange > 0
                
                return (
                  <tr key={analysis.id} className="hover:bg-white/5 transition-colors">
                    <td className="p-4">
                      <div>
                        <p className="font-medium text-white">{analysis.farm_name}</p>
                        <p className="text-sm text-gray-400">
                          {formatDistanceToNow(analysis.date, { addSuffix: true })}
                        </p>
                      </div>
                    </td>
                    <td className="p-4">
                      <div className="flex items-center gap-2 text-gray-400">
                        <Calendar className="h-4 w-4" />
                        <span>{analysis.date.toLocaleDateString()}</span>
                      </div>
                    </td>
                    <td className="p-4">
                      <span className={`text-2xl font-bold ${getHealthColor(analysis.health_score)}`}>
                        {analysis.health_score}%
                      </span>
                    </td>
                    <td className="p-4">
                      <div className={`flex items-center gap-1 ${isPositive ? 'text-emerald-500' : 'text-red-500'}`}>
                        {isPositive ? (
                          <TrendingUp className="h-4 w-4" />
                        ) : (
                          <TrendingDown className="h-4 w-4" />
                        )}
                        <span className="font-medium">
                          {isPositive ? '+' : ''}{scoreChange}%
                        </span>
                      </div>
                    </td>
                    <td className="p-4">
                      <p className="text-sm text-gray-300 max-w-md truncate">
                        {analysis.findings}
                      </p>
                    </td>
                    <td className="p-4">
                      <Badge className={`${getStatusBadge(analysis.status)} border`}>
                        {analysis.status}
                      </Badge>
                    </td>
                    <td className="p-4">
                      <Link href={`/farms/${analysis.farm_id}`}>
                        <Button 
                          size="sm" 
                          variant="outline"
                          className="border-white/20 text-white hover:bg-emerald-600 hover:border-emerald-600"
                        >
                          View Details
                        </Button>
                      </Link>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>

        {filteredAnalyses.length === 0 && (
          <div className="p-12 text-center">
            <Activity className="h-16 w-16 mx-auto mb-4 text-gray-600" />
            <h3 className="text-xl font-semibold text-white mb-2">
              No analyses found
            </h3>
            <p className="text-gray-400">
              Try adjusting your search or filters
            </p>
          </div>
        )}
      </Card>

      {/* Stats Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="bg-zinc-900 border-white/10 p-6">
          <p className="text-sm text-gray-400 mb-2">Total Analyses</p>
          <p className="text-3xl font-bold text-white">{mockAnalyses.length}</p>
        </Card>
        <Card className="bg-zinc-900 border-white/10 p-6">
          <p className="text-sm text-gray-400 mb-2">Avg Health Score</p>
          <p className="text-3xl font-bold text-emerald-500">83%</p>
        </Card>
        <Card className="bg-zinc-900 border-white/10 p-6">
          <p className="text-sm text-gray-400 mb-2">Improving Farms</p>
          <p className="text-3xl font-bold text-emerald-500">2</p>
        </Card>
        <Card className="bg-zinc-900 border-white/10 p-6">
          <p className="text-sm text-gray-400 mb-2">Needs Attention</p>
          <p className="text-3xl font-bold text-yellow-500">1</p>
        </Card>
      </div>
    </div>
  )
}
