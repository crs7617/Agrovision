'use client'

import { useQuery } from '@tanstack/react-query'
import { Card } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Sprout, TrendingUp, AlertTriangle, BarChart3 } from 'lucide-react'
import { getCurrentUser } from '@/lib/supabase/client'
import { useEffect, useState } from 'react'
import type { Farm } from '@/types'

export default function DashboardPage() {
  const [userId, setUserId] = useState<string | null>(null)

  useEffect(() => {
    getCurrentUser().then((user) => {
      if (user) setUserId(user.id)
    })
  }, [])

  const { data: farms, isLoading } = useQuery({
    queryKey: ['farms', userId],
    queryFn: async () => {
      if (!userId) return []
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/farms?user_id=${userId}`)
      if (!res.ok) throw new Error('Failed to fetch farms')
      return res.json()
    },
    enabled: !!userId,
  })

  // Fetch health stats for all farms
  const { data: healthStats } = useQuery({
    queryKey: ['health-stats', farms],
    queryFn: async () => {
      if (!farms || farms.length === 0) return null
      
      const healthPromises = farms.map(async (farm: Farm) => {
        try {
          const res = await fetch(
            `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/farms/${farm.id}/trends?index=ndvi&days=7`
          )
          if (!res.ok) return { farmId: farm.id, avgHealth: 75 }
          const data = await res.json()
          const avgHealth = data.latest_value ? Math.round(data.latest_value * 100) : 75
          return { farmId: farm.id, avgHealth }
        } catch {
          return { farmId: farm.id, avgHealth: 75 }
        }
      })
      
      const results = await Promise.all(healthPromises)
      const totalHealth = results.reduce((sum, r) => sum + r.avgHealth, 0)
      const avgHealth = Math.round(totalHealth / results.length)
      
      return { avgHealth, farmHealthMap: results }
    },
    enabled: !!farms && farms.length > 0,
  })

  const stats = [
    {
      title: 'Total Farms',
      value: farms?.length || 0,
      icon: Sprout,
      color: 'text-emerald-500',
      bg: 'bg-emerald-500/10',
    },
    {
      title: 'Avg Health Score',
      value: `${healthStats?.avgHealth || 75}%`,
      icon: TrendingUp,
      color: 'text-blue-500',
      bg: 'bg-blue-500/10',
    },
    {
      title: 'Active Analyses',
      value: farms?.length || 0,
      icon: BarChart3,
      color: 'text-purple-500',
      bg: 'bg-purple-500/10',
    },
    {
      title: 'Alerts',
      value: 2,
      icon: AlertTriangle,
      color: 'text-yellow-500',
      bg: 'bg-yellow-500/10',
    },
  ]

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">
          Welcome back! 👋
        </h1>
        <p className="text-gray-400">
          Here&apos;s what&apos;s happening with your farms today
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => (
          <Card
            key={stat.title}
            className="bg-zinc-900 border-white/10 p-6 hover:border-emerald-500/30 transition-colors"
          >
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-gray-400 mb-1">{stat.title}</p>
                <p className="text-3xl font-bold text-white">{stat.value}</p>
              </div>
              <div className={`p-3 rounded-lg ${stat.bg}`}>
                <stat.icon className={`h-6 w-6 ${stat.color}`} />
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Recent Farms */}
      <div>
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-white">Recent Farms</h2>
        </div>

        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3].map((i) => (
              <Card key={i} className="bg-zinc-900 border-white/10 p-6">
                <Skeleton className="h-4 w-32 mb-4 bg-white/10" />
                <Skeleton className="h-8 w-20 mb-2 bg-white/10" />
                <Skeleton className="h-4 w-full bg-white/10" />
              </Card>
            ))}
          </div>
        ) : farms && farms.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {farms.slice(0, 3).map((farm: Farm) => {
              const farmHealth = healthStats?.farmHealthMap?.find(
                (h: { farmId: string; avgHealth: number }) => h.farmId === farm.id
              )
              const healthScore = farmHealth?.avgHealth || 75
              const healthColor =
                healthScore >= 80
                  ? 'text-emerald-500'
                  : healthScore >= 60
                  ? 'text-yellow-500'
                  : 'text-red-500'

              return (
                <Card
                  key={farm.id}
                  className="bg-zinc-900 border-white/10 p-6 hover:border-emerald-500/50 transition-all cursor-pointer group"
                  onClick={() => window.location.href = `/farms/${farm.id}`}
                >
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h3 className="text-lg font-semibold text-white group-hover:text-emerald-500 transition-colors">
                        {farm.name}
                      </h3>
                      <p className="text-sm text-gray-400">{farm.crop_type}</p>
                    </div>
                    <div className={`text-2xl font-bold ${healthColor}`}>
                      {healthScore}%
                    </div>
                  </div>
                  <div className="space-y-2 text-sm text-gray-400">
                    <div>📍 {farm.lat?.toFixed(2) ?? 'N/A'}, {farm.lng?.toFixed(2) ?? 'N/A'}</div>
                    <div>📏 {farm.area ?? 'N/A'} hectares</div>
                  </div>
                </Card>
              )
            })}
          </div>
        ) : (
          <Card className="bg-zinc-900 border-white/10 p-12 text-center">
            <Sprout className="h-16 w-16 mx-auto mb-4 text-gray-600" />
            <h3 className="text-xl font-semibold text-white mb-2">
              No farms yet
            </h3>
            <p className="text-gray-400">
              Add your first farm to start monitoring
            </p>
          </Card>
        )}
      </div>
    </div>
  )
}
