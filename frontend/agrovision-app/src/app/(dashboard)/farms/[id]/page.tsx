'use client'

import { useQuery } from '@tanstack/react-query'
import { useParams } from 'next/navigation'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Sprout,
  MapPin,
  Calendar,
  TrendingUp,
  Activity,
  Droplets,
  Sun,
  Wind,
} from 'lucide-react'
import { LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import dynamic from 'next/dynamic'

// Dynamic import for Leaflet map (client-side only)
const FarmMap = dynamic(() => import('@/components/FarmMap'), {
  ssr: false,
  loading: () => (
    <div className="w-full h-[400px] bg-zinc-900 rounded-lg flex items-center justify-center">
      <p className="text-gray-400">Loading map...</p>
    </div>
  ),
})

const USER_ID = '00000000-0000-0000-0000-000000000001'
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://agrovision-backend.onrender.com'

// Mock data - replace with real API calls
const mockHistoricalData = [
  { date: '2025-01-01', ndvi: 0.65, evi: 0.45, savi: 0.55 },
  { date: '2025-01-08', ndvi: 0.68, evi: 0.48, savi: 0.58 },
  { date: '2025-01-15', ndvi: 0.72, evi: 0.52, savi: 0.62 },
  { date: '2025-01-22', ndvi: 0.75, evi: 0.55, savi: 0.65 },
  { date: '2025-01-29', ndvi: 0.73, evi: 0.53, savi: 0.63 },
  { date: '2025-02-05', ndvi: 0.70, evi: 0.50, savi: 0.60 },
  { date: '2025-02-12', ndvi: 0.74, evi: 0.54, savi: 0.64 },
]

const mockHealthZones = [
  { name: 'Excellent', value: 35, color: '#10b981' },
  { name: 'Good', value: 40, color: '#3b82f6' },
  { name: 'Moderate', value: 20, color: '#eab308' },
  { name: 'Poor', value: 5, color: '#ef4444' },
]

const mockRecommendations = [
  {
    id: 1,
    priority: 'High',
    title: 'Irrigation Needed in North Zone',
    description: 'NDVI values show water stress in the northern 15% of the farm. Increase irrigation frequency.',
    affectedArea: 15,
    impact: '+8% yield',
    completed: false,
  },
  {
    id: 2,
    priority: 'Medium',
    title: 'Nutrient Deficiency Detected',
    description: 'EVI analysis suggests nitrogen deficiency in central areas. Consider fertilizer application.',
    affectedArea: 25,
    impact: '+12% yield',
    completed: false,
  },
  {
    id: 3,
    priority: 'Low',
    title: 'Monitor Pest Activity',
    description: 'Slight decrease in health score. Regular monitoring recommended for early pest detection.',
    affectedArea: 10,
    impact: '+5% yield',
    completed: true,
  },
]

export default function FarmDetailPage() {
  const params = useParams()
  const farmId = params.id as string

  const { data: farm, isLoading: farmLoading } = useQuery({
    queryKey: ['farm', farmId],
    queryFn: async () => {
      const res = await fetch(`${API_BASE_URL}/api/farms/${farmId}?user_id=${USER_ID}`)
      if (!res.ok) throw new Error('Failed to fetch farm')
      return res.json()
    },
  })

  if (farmLoading) {
    return (
      <div className="max-w-7xl mx-auto space-y-6">
        <Skeleton className="h-12 w-64 bg-white/10" />
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {[1, 2, 3, 4].map((i) => (
            <Skeleton key={i} className="h-32 bg-white/10" />
          ))}
        </div>
        <Skeleton className="h-96 bg-white/10" />
      </div>
    )
  }

  if (!farm) {
    return (
      <div className="max-w-7xl mx-auto">
        <Card className="bg-zinc-900 border-white/10 p-12 text-center">
          <h2 className="text-2xl font-bold text-white mb-2">Farm not found</h2>
          <p className="text-gray-400">The farm you&apos;re looking for doesn&apos;t exist.</p>
        </Card>
      </div>
    )
  }

  const healthScore = 75
  const ndviValue = 0.74
  const eviValue = 0.54
  const saviValue = 0.64

  const getHealthColor = (score: number) => {
    if (score >= 80) return 'text-emerald-500 bg-emerald-500/10'
    if (score >= 60) return 'text-yellow-500 bg-yellow-500/10'
    return 'text-red-500 bg-red-500/10'
  }

  const getIndexColor = (value: number) => {
    if (value >= 0.7) return 'text-emerald-500'
    if (value >= 0.5) return 'text-yellow-500'
    return 'text-red-500'
  }

  const getPriorityColor = (priority: string) => {
    if (priority === 'High') return 'bg-red-500/10 text-red-500 border-red-500/20'
    if (priority === 'Medium') return 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20'
    return 'bg-blue-500/10 text-blue-500 border-blue-500/20'
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">{farm.name}</h1>
          <div className="flex items-center gap-4 text-gray-400">
            <div className="flex items-center gap-2">
              <Sprout className="h-5 w-5" />
              <span>{farm.crop_type}</span>
            </div>
            <div className="flex items-center gap-2">
              <MapPin className="h-5 w-5" />
              <span>{farm.lat?.toFixed(4) ?? 'N/A'}, {farm.lng?.toFixed(4) ?? 'N/A'}</span>
            </div>
            <div className="flex items-center gap-2">
              <Calendar className="h-5 w-5" />
              <span>{farm.area ?? 'N/A'} hectares</span>
            </div>
          </div>
        </div>
        <Button className="bg-emerald-600 hover:bg-emerald-700 text-white">
          <Activity className="mr-2 h-4 w-4" />
          Run New Analysis
        </Button>
      </div>

      {/* Health Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="bg-zinc-900 border-white/10 p-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <p className="text-sm text-gray-400 mb-1">Health Score</p>
              <p className={`text-4xl font-bold ${getHealthColor(healthScore).split(' ')[0]}`}>
                {healthScore}%
              </p>
            </div>
            <div className={`p-3 rounded-lg ${getHealthColor(healthScore)}`}>
              <TrendingUp className="h-6 w-6" />
            </div>
          </div>
          <div className="flex items-center gap-1 text-sm text-emerald-500">
            <TrendingUp className="h-4 w-4" />
            <span>+5% from last week</span>
          </div>
        </Card>

        <Card className="bg-zinc-900 border-white/10 p-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <p className="text-sm text-gray-400 mb-1">NDVI</p>
              <p className={`text-4xl font-bold ${getIndexColor(ndviValue)}`}>
                {ndviValue.toFixed(2)}
              </p>
            </div>
            <div className="p-3 rounded-lg bg-green-500/10">
              <Droplets className="h-6 w-6 text-green-500" />
            </div>
          </div>
          <p className="text-xs text-gray-500">Excellent vegetation health</p>
        </Card>

        <Card className="bg-zinc-900 border-white/10 p-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <p className="text-sm text-gray-400 mb-1">EVI</p>
              <p className={`text-4xl font-bold ${getIndexColor(eviValue)}`}>
                {eviValue.toFixed(2)}
              </p>
            </div>
            <div className="p-3 rounded-lg bg-blue-500/10">
              <Sun className="h-6 w-6 text-blue-500" />
            </div>
          </div>
          <p className="text-xs text-gray-500">Good canopy cover</p>
        </Card>

        <Card className="bg-zinc-900 border-white/10 p-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <p className="text-sm text-gray-400 mb-1">SAVI</p>
              <p className={`text-4xl font-bold ${getIndexColor(saviValue)}`}>
                {saviValue.toFixed(2)}
              </p>
            </div>
            <div className="p-3 rounded-lg bg-purple-500/10">
              <Wind className="h-6 w-6 text-purple-500" />
            </div>
          </div>
          <p className="text-xs text-gray-500">Soil-adjusted index</p>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="trends" className="space-y-6">
        <TabsList className="bg-zinc-900 border border-white/10">
          <TabsTrigger value="trends" className="data-[state=active]:bg-emerald-600 data-[state=active]:text-white">
            Historical Trends
          </TabsTrigger>
          <TabsTrigger value="zones" className="data-[state=active]:bg-emerald-600 data-[state=active]:text-white">
            Health Analysis
          </TabsTrigger>
          <TabsTrigger value="recommendations" className="data-[state=active]:bg-emerald-600 data-[state=active]:text-white">
            Recommendations
          </TabsTrigger>
          <TabsTrigger value="satellite" className="data-[state=active]:bg-emerald-600 data-[state=active]:text-white">
            Satellite Imagery
          </TabsTrigger>
        </TabsList>

        <TabsContent value="trends" className="space-y-6">
          <Card className="bg-zinc-900 border-white/10 p-6">
            <h3 className="text-xl font-bold text-white mb-6">Vegetation Index Trends (90 Days)</h3>
            <ResponsiveContainer width="100%" height={400}>
              <LineChart data={mockHistoricalData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#ffffff20" />
                <XAxis dataKey="date" stroke="#9ca3af" />
                <YAxis stroke="#9ca3af" />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#18181b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                  labelStyle={{ color: '#fff' }}
                />
                <Legend />
                <Line type="monotone" dataKey="ndvi" stroke="#10b981" strokeWidth={2} name="NDVI" />
                <Line type="monotone" dataKey="evi" stroke="#3b82f6" strokeWidth={2} name="EVI" />
                <Line type="monotone" dataKey="savi" stroke="#a855f7" strokeWidth={2} name="SAVI" />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </TabsContent>

        <TabsContent value="zones" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="bg-zinc-900 border-white/10 p-6">
              <h3 className="text-xl font-bold text-white mb-6">Health Distribution</h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={mockHealthZones}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, value }) => `${name}: ${value}%`}
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {mockHealthZones.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#18181b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </Card>

            <Card className="bg-zinc-900 border-white/10 p-6">
              <h3 className="text-xl font-bold text-white mb-6">Zone Breakdown</h3>
              <div className="space-y-4">
                {mockHealthZones.map((zone) => (
                  <div key={zone.name} className="flex items-center justify-between p-4 rounded-lg bg-black/50">
                    <div className="flex items-center gap-3">
                      <div className="w-4 h-4 rounded-full" style={{ backgroundColor: zone.color }} />
                      <span className="text-white font-medium">{zone.name}</span>
                    </div>
                    <span className="text-2xl font-bold text-white">{zone.value}%</span>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="recommendations" className="space-y-4">
          {mockRecommendations.map((rec) => (
            <Card key={rec.id} className={`bg-zinc-900 border-white/10 p-6 ${rec.completed ? 'opacity-60' : ''}`}>
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getPriorityColor(rec.priority)}`}>
                      {rec.priority} Priority
                    </span>
                    {rec.completed && (
                      <span className="px-3 py-1 rounded-full text-xs font-medium bg-green-500/10 text-green-500 border border-green-500/20">
                        Completed
                      </span>
                    )}
                  </div>
                  <h4 className="text-xl font-bold text-white mb-2">{rec.title}</h4>
                  <p className="text-gray-400 mb-4">{rec.description}</p>
                  <div className="flex items-center gap-6 text-sm">
                    <span className="text-gray-500">
                      Affected Area: <span className="text-white font-medium">{rec.affectedArea}%</span>
                    </span>
                    <span className="text-gray-500">
                      Est. Impact: <span className="text-emerald-500 font-medium">{rec.impact}</span>
                    </span>
                  </div>
                </div>
                {!rec.completed && (
                  <Button className="bg-emerald-600 hover:bg-emerald-700 text-white">
                    Mark Complete
                  </Button>
                )}
              </div>
            </Card>
          ))}
        </TabsContent>

        <TabsContent value="satellite">
          <Card className="bg-zinc-900 border-white/10 p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-white">Satellite Imagery & Location</h3>
              <Button variant="outline" className="border-white/20 text-white hover:bg-white/5">
                View Fullscreen
              </Button>
            </div>
            {farm && (
              <FarmMap
                lat={farm.lat}
                lng={farm.lng}
                farmName={farm.name}
                area={farm.area}
                healthScore={healthScore}
              />
            )}
            <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
              <Card className="bg-black/50 border-white/10 p-4">
                <p className="text-sm text-gray-400 mb-1">Latitude</p>
                <p className="text-lg font-bold text-white">{farm?.lat?.toFixed(6) ?? 'N/A'}</p>
              </Card>
              <Card className="bg-black/50 border-white/10 p-4">
                <p className="text-sm text-gray-400 mb-1">Longitude</p>
                <p className="text-lg font-bold text-white">{farm?.lng?.toFixed(6) ?? 'N/A'}</p>
              </Card>
              <Card className="bg-black/50 border-white/10 p-4">
                <p className="text-sm text-gray-400 mb-1">Total Area</p>
                <p className="text-lg font-bold text-white">{farm?.area} hectares</p>
              </Card>
            </div>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
