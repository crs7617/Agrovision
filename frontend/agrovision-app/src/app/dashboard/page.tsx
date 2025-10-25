'use client';

import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { Sprout, BarChart3, TrendingUp, AlertCircle, Plus } from 'lucide-react';

const API_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
const USER_ID = '00000000-0000-0000-0000-000000000001';

export default function DashboardPage() {
  const { data: farms, isLoading } = useQuery({
    queryKey: ['farms'],
    queryFn: async () => {
      const res = await fetch(`${API_URL}/api/farms?user_id=${USER_ID}`);
      if (!res.ok) throw new Error('Failed to fetch farms');
      return res.json();
    },
  });

  const getHealthColor = (score?: number) => {
    if (!score) return 'text-slate-500';
    if (score >= 80) return 'text-emerald-500';
    if (score >= 60) return 'text-yellow-500';
    return 'text-red-500';
  };

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Header */}
      <div className="border-b border-slate-800 bg-slate-900/50 backdrop-blur">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold">Dashboard</h1>
              <p className="text-slate-400 mt-1">Welcome back! Here&apos;s your farm overview</p>
            </div>
            <Link href="/farms/new">
              <Button className="bg-emerald-600 hover:bg-emerald-700">
                <Plus className="mr-2 h-4 w-4" />
                Add Farm
              </Button>
            </Link>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Row */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="bg-slate-900 border-slate-800 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">Total Farms</p>
                <p className="text-3xl font-bold mt-2">{farms?.length || 0}</p>
              </div>
              <div className="w-12 h-12 bg-emerald-500/10 rounded-lg flex items-center justify-center">
                <Sprout className="h-6 w-6 text-emerald-500" />
              </div>
            </div>
          </Card>

          <Card className="bg-slate-900 border-slate-800 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">Avg Health Score</p>
                <p className="text-3xl font-bold mt-2">
                  {farms?.length > 0 ? '75%' : '0%'}
                </p>
              </div>
              <div className="w-12 h-12 bg-blue-500/10 rounded-lg flex items-center justify-center">
                <BarChart3 className="h-6 w-6 text-blue-500" />
              </div>
            </div>
          </Card>

          <Card className="bg-slate-900 border-slate-800 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">Active Analyses</p>
                <p className="text-3xl font-bold mt-2">12</p>
              </div>
              <div className="w-12 h-12 bg-purple-500/10 rounded-lg flex items-center justify-center">
                <TrendingUp className="h-6 w-6 text-purple-500" />
              </div>
            </div>
          </Card>

          <Card className="bg-slate-900 border-slate-800 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">Alerts</p>
                <p className="text-3xl font-bold mt-2">2</p>
              </div>
              <div className="w-12 h-12 bg-red-500/10 rounded-lg flex items-center justify-center">
                <AlertCircle className="h-6 w-6 text-red-500" />
              </div>
            </div>
          </Card>
        </div>

        {/* Farms Grid */}
        <div>
          <h2 className="text-2xl font-semibold mb-6">Your Farms</h2>
          {isLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[...Array(3)].map((_, i) => (
                <Card key={i} className="bg-slate-900 border-slate-800 p-6">
                  <Skeleton className="h-6 w-3/4 mb-4" />
                  <Skeleton className="h-4 w-1/2 mb-6" />
                  <Skeleton className="h-4 w-full mb-2" />
                  <Skeleton className="h-4 w-2/3" />
                </Card>
              ))}
            </div>
          ) : farms && farms.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {farms.map((farm: any) => (
                <Link key={farm.id} href={`/farms/${farm.id}`}>
                  <Card className="bg-slate-900 border-slate-800 p-6 hover:border-emerald-500/50 transition-all group cursor-pointer">
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <h3 className="text-xl font-semibold group-hover:text-emerald-400 transition-colors">
                          {farm.name}
                        </h3>
                        <p className="text-sm text-emerald-400 uppercase tracking-wide mt-1">
                          {farm.crop_type}
                        </p>
                      </div>
                      <div className={`text-2xl font-bold ${getHealthColor(75)}`}>
                        75%
                      </div>
                    </div>
                    <div className="space-y-2 text-sm text-slate-400">
                      <div className="flex justify-between">
                        <span>Area:</span>
                        <span className="text-slate-300">{farm.area} hectares</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Location:</span>
                        <span className="text-slate-300">
                          {farm.latitude.toFixed(2)}, {farm.longitude.toFixed(2)}
                        </span>
                      </div>
                    </div>
                  </Card>
                </Link>
              ))}
            </div>
          ) : (
            <Card className="bg-slate-900 border-slate-800 p-12 text-center">
              <Sprout className="h-16 w-16 text-slate-600 mx-auto mb-4" />
              <h3 className="text-xl font-semibold mb-2">No farms yet</h3>
              <p className="text-slate-400 mb-6">
                Get started by adding your first farm to begin monitoring
              </p>
              <Link href="/farms/new">
                <Button className="bg-emerald-600 hover:bg-emerald-700">
                  <Plus className="mr-2 h-4 w-4" />
                  Add Your First Farm
                </Button>
              </Link>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
