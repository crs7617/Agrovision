'use client'

import { useEffect, useState } from 'react'
import { MapContainer, TileLayer, Marker, Popup, Circle } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import L from 'leaflet'

// Fix for default marker icons in react-leaflet
const iconDefault = L.Icon.Default.prototype as unknown as Record<string, unknown>
delete iconDefault._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
})

interface FarmMapProps {
  lat: number
  lng: number
  farmName: string
  area?: number
  healthScore?: number
}

export default function FarmMap({ lat, lng, farmName, area, healthScore = 75 }: FarmMapProps) {
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    // This is a valid use case for hydration mismatch prevention
    const timer = setTimeout(() => setMounted(true), 0)
    return () => clearTimeout(timer)
  }, [])

  if (!mounted) {
    return (
      <div className="w-full h-[400px] bg-zinc-900 rounded-lg flex items-center justify-center">
        <p className="text-gray-400">Loading map...</p>
      </div>
    )
  }

  // Calculate circle radius based on area (approximate km from hectares)
  const circleRadius = area ? Math.sqrt(area * 10000) : 200 // Default 200m radius

  // Color based on health score
  const getHealthColor = (score: number) => {
    if (score >= 80) return '#10b981' // emerald-500
    if (score >= 60) return '#fbbf24' // amber-500
    return '#ef4444' // red-500
  }

  return (
    <div className="w-full h-[400px] rounded-lg overflow-hidden border border-white/10">
      <MapContainer
        center={[lat, lng]}
        zoom={15}
        style={{ height: '100%', width: '100%' }}
        className="z-0"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        {/* Farm boundary circle */}
        <Circle
          center={[lat, lng]}
          radius={circleRadius}
          pathOptions={{
            color: getHealthColor(healthScore),
            fillColor: getHealthColor(healthScore),
            fillOpacity: 0.2,
            weight: 2,
          }}
        />
        
        {/* Farm center marker */}
        <Marker position={[lat, lng]}>
          <Popup>
            <div className="text-black">
              <h3 className="font-bold">{farmName}</h3>
              {area && <p>Area: {area} hectares</p>}
              {healthScore && <p>Health Score: {healthScore}%</p>}
              <p className="text-xs text-gray-600 mt-1">
                {lat.toFixed(6)}, {lng.toFixed(6)}
              </p>
            </div>
          </Popup>
        </Marker>
      </MapContainer>
    </div>
  )
}
