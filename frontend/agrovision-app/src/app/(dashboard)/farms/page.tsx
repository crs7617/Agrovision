'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import {
  Plus,
  Search,
  Grid3x3,
  List,
  MapPin,
  Calendar,
  Sprout,
} from 'lucide-react'
import toast from 'react-hot-toast'
import { formatDistanceToNow } from 'date-fns'
import type { Farm, CreateFarmData } from '@/types'

const USER_ID = '00000000-0000-0000-0000-000000000001'

const CROP_TYPES = [
  'Wheat',
  'Rice',
  'Corn',
  'Cotton',
  'Soybean',
  'Sugarcane',
  'Barley',
  'Potato',
  'Tomato',
  'Other',
]

export default function FarmsPage() {
  const queryClient = useQueryClient()
  const [searchQuery, setSearchQuery] = useState('')
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [dialogOpen, setDialogOpen] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    crop_type: '',
    latitude: '',
    longitude: '',
    area: '',
    description: '',
  })

  // Fetch farms
  const { data: farms, isLoading } = useQuery({
    queryKey: ['farms'],
    queryFn: async () => {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/farms?user_id=${USER_ID}`)
      if (!res.ok) throw new Error('Failed to fetch farms')
      return res.json()
    },
  })

  // Create farm mutation
  const createFarm = useMutation({
    mutationFn: async (data: CreateFarmData) => {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/farms`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: USER_ID,
          name: data.name,
          crop_type: data.crop_type,
          lat: parseFloat(data.latitude),
          lng: parseFloat(data.longitude),
          area: parseFloat(data.area),
        }),
      })
      if (!res.ok) throw new Error('Failed to create farm')
      return res.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['farms'] })
      toast.success('Farm created successfully!')
      setDialogOpen(false)
      setFormData({
        name: '',
        crop_type: '',
        latitude: '',
        longitude: '',
        area: '',
        description: '',
      })
    },
    onError: () => {
      toast.error('Failed to create farm')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.name || !formData.crop_type || !formData.latitude || !formData.longitude || !formData.area) {
      toast.error('Please fill in all required fields')
      return
    }
    createFarm.mutate(formData)
  }

  const filteredFarms = farms?.filter((farm: Farm) =>
    farm.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    farm.crop_type.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const getHealthColor = (score: number) => {
    if (score >= 80) return 'text-emerald-500 bg-emerald-500/10'
    if (score >= 60) return 'text-yellow-500 bg-yellow-500/10'
    return 'text-red-500 bg-red-500/10'
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">My Farms</h1>
          <p className="text-gray-400 mt-1">
            {farms?.length || 0} farm{farms?.length !== 1 ? 's' : ''} total
          </p>
        </div>

        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button className="bg-emerald-600 hover:bg-emerald-700 text-white">
              <Plus className="mr-2 h-4 w-4" />
              Add New Farm
            </Button>
          </DialogTrigger>
          <DialogContent className="bg-zinc-900 border-white/10 text-white sm:max-w-md">
            <DialogHeader>
              <DialogTitle className="text-white">Add New Farm</DialogTitle>
              <DialogDescription className="text-gray-400">
                Enter your farm details to start monitoring
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4 mt-4">
              <div className="space-y-2">
                <Label htmlFor="name" className="text-white">Farm Name *</Label>
                <Input
                  id="name"
                  placeholder="e.g., North Field"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="bg-black border-white/20 text-white placeholder:text-gray-500"
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="crop_type" className="text-white">Crop Type *</Label>
                <Select
                  value={formData.crop_type}
                  onValueChange={(value) => setFormData({ ...formData, crop_type: value })}
                >
                  <SelectTrigger className="bg-black border-white/20 text-white">
                    <SelectValue placeholder="Select crop type" />
                  </SelectTrigger>
                  <SelectContent className="bg-zinc-900 border-white/10">
                    {CROP_TYPES.map((crop) => (
                      <SelectItem key={crop} value={crop} className="text-white hover:bg-white/5">
                        {crop}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="latitude" className="text-white">Latitude *</Label>
                  <Input
                    id="latitude"
                    type="number"
                    step="any"
                    placeholder="e.g., 17.385"
                    value={formData.latitude}
                    onChange={(e) => setFormData({ ...formData, latitude: e.target.value })}
                    className="bg-black border-white/20 text-white placeholder:text-gray-500"
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="longitude" className="text-white">Longitude *</Label>
                  <Input
                    id="longitude"
                    type="number"
                    step="any"
                    placeholder="e.g., 78.486"
                    value={formData.longitude}
                    onChange={(e) => setFormData({ ...formData, longitude: e.target.value })}
                    className="bg-black border-white/20 text-white placeholder:text-gray-500"
                    required
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="area" className="text-white">Area (hectares) *</Label>
                <Input
                  id="area"
                  type="number"
                  step="any"
                  placeholder="e.g., 50"
                  value={formData.area}
                  onChange={(e) => setFormData({ ...formData, area: e.target.value })}
                  className="bg-black border-white/20 text-white placeholder:text-gray-500"
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="description" className="text-white">Description (optional)</Label>
                <Textarea
                  id="description"
                  placeholder="Add any notes about this farm..."
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="bg-black border-white/20 text-white placeholder:text-gray-500"
                  rows={3}
                />
              </div>

              <div className="flex gap-3 pt-4">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setDialogOpen(false)}
                  className="flex-1 border-white/20 text-white hover:bg-white/5"
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  className="flex-1 bg-emerald-600 hover:bg-emerald-700 text-white"
                  disabled={createFarm.isPending}
                >
                  {createFarm.isPending ? 'Creating...' : 'Create Farm'}
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Search and View Toggle */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
          <Input
            placeholder="Search farms by name or crop type..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10 bg-zinc-900 border-white/20 text-white placeholder:text-gray-500"
          />
        </div>
        <div className="flex gap-2">
          <Button
            variant={viewMode === 'grid' ? 'default' : 'outline'}
            size="icon"
            onClick={() => setViewMode('grid')}
            className={viewMode === 'grid' ? 'bg-emerald-600 hover:bg-emerald-700' : 'border-white/20 text-white hover:bg-white/5'}
          >
            <Grid3x3 className="h-5 w-5" />
          </Button>
          <Button
            variant={viewMode === 'list' ? 'default' : 'outline'}
            size="icon"
            onClick={() => setViewMode('list')}
            className={viewMode === 'list' ? 'bg-emerald-600 hover:bg-emerald-700' : 'border-white/20 text-white hover:bg-white/5'}
          >
            <List className="h-5 w-5" />
          </Button>
        </div>
      </div>

      {/* Farms Grid/List */}
      {isLoading ? (
        <div className={viewMode === 'grid' ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6' : 'space-y-4'}>
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <Card key={i} className="bg-zinc-900 border-white/10 p-6">
              <Skeleton className="h-6 w-32 mb-4 bg-white/10" />
              <Skeleton className="h-10 w-20 mb-4 bg-white/10" />
              <Skeleton className="h-4 w-full mb-2 bg-white/10" />
              <Skeleton className="h-4 w-3/4 bg-white/10" />
            </Card>
          ))}
        </div>
      ) : filteredFarms && filteredFarms.length > 0 ? (
        <div className={viewMode === 'grid' ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6' : 'space-y-4'}>
          {filteredFarms.map((farm: Farm) => {
            const healthScore = 75 // Placeholder
            const colorClass = getHealthColor(healthScore)
            
            return (
              <Link key={farm.id} href={`/farms/${farm.id}`}>
                <Card className="bg-zinc-900 border-white/10 p-6 hover:border-emerald-500/50 transition-all cursor-pointer group h-full">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <h3 className="text-xl font-bold text-white group-hover:text-emerald-500 transition-colors mb-1">
                        {farm.name}
                      </h3>
                      <div className="flex items-center gap-2 text-sm text-gray-400">
                        <Sprout className="h-4 w-4" />
                        {farm.crop_type}
                      </div>
                    </div>
                    <div className={`px-3 py-1 rounded-lg ${colorClass} font-bold text-lg`}>
                      {healthScore}%
                    </div>
                  </div>

                  <div className="space-y-2 text-sm text-gray-400">
                    <div className="flex items-center gap-2">
                      <MapPin className="h-4 w-4" />
                      <span>{farm.lat?.toFixed(4) ?? 'N/A'}, {farm.lng?.toFixed(4) ?? 'N/A'}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span>📏</span>
                      <span>{farm.area ?? 'N/A'} hectares</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Calendar className="h-4 w-4" />
                      <span>Added {formatDistanceToNow(new Date(farm.created_at), { addSuffix: true })}</span>
                    </div>
                  </div>

                  <Button
                    className="w-full mt-4 bg-white/5 hover:bg-emerald-600 text-white border-0"
                    variant="outline"
                  >
                    View Details
                  </Button>
                </Card>
              </Link>
            )
          })}
        </div>
      ) : (
        <Card className="bg-zinc-900 border-white/10 p-12 text-center">
          <Sprout className="h-20 w-20 mx-auto mb-6 text-gray-600" />
          <h3 className="text-2xl font-bold text-white mb-2">
            {searchQuery ? 'No farms found' : 'No farms yet'}
          </h3>
          <p className="text-gray-400 mb-6">
            {searchQuery
              ? 'Try adjusting your search terms'
              : 'Add your first farm to start monitoring crop health'}
          </p>
          {!searchQuery && (
            <Button
              className="bg-emerald-600 hover:bg-emerald-700 text-white"
              onClick={() => setDialogOpen(true)}
            >
              <Plus className="mr-2 h-4 w-4" />
              Add Your First Farm
            </Button>
          )}
        </Card>
      )}
    </div>
  )
}
