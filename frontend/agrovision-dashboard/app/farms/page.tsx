'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import { Plus, Trash2, MapPin, TrendingUp } from 'lucide-react';
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const USER_ID = '00000000-0000-0000-0000-000000000001';

interface Farm {
  id: string;
  name: string;
  crop_type: string;
  latitude: number;
  longitude: number;
  area: number;
  health_score?: number;
  created_at: string;
}

export default function FarmsPage() {
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [newFarm, setNewFarm] = useState({
    name: '',
    crop_type: '',
    latitude: '',
    longitude: '',
    area: ''
  });
  
  const queryClient = useQueryClient();

  const { data: farms = [], isLoading } = useQuery({
    queryKey: ['farms'],
    queryFn: async () => {
      const { data } = await axios.get(`${API_URL}/api/farms?user_id=${USER_ID}`);
      return data;
    }
  });

  const createFarm = useMutation({
    mutationFn: async (farmData: any) => {
      const { data } = await axios.post(`${API_URL}/api/farms`, {
        ...farmData,
        user_id: USER_ID
      });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['farms'] });
      setIsAddModalOpen(false);
      setNewFarm({ name: '', crop_type: '', latitude: '', longitude: '', area: '' });
    }
  });

  const deleteFarm = useMutation({
    mutationFn: async (farmId: string) => {
      await axios.delete(`${API_URL}/api/farms/${farmId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['farms'] });
    }
  });

  const getHealthColor = (score?: number) => {
    if (!score) return 'bg-gray-700';
    if (score >= 80) return 'bg-emerald-500';
    if (score >= 60) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createFarm.mutate({
      name: newFarm.name,
      crop_type: newFarm.crop_type,
      latitude: parseFloat(newFarm.latitude),
      longitude: parseFloat(newFarm.longitude),
      area: parseFloat(newFarm.area)
    });
  };

  return (
    <div className="min-h-screen bg-black text-white p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-12">
          <div>
            <h1 className="text-4xl font-bold mb-2">My Farms</h1>
            <p className="text-gray-400">Manage and monitor your agricultural sites</p>
          </div>
          <button
            onClick={() => setIsAddModalOpen(true)}
            className="flex items-center gap-2 bg-emerald-600 hover:bg-emerald-700 px-6 py-3 rounded-lg transition-colors"
          >
            <Plus size={20} />
            Add Farm
          </button>
        </div>

        {/* Farm Grid */}
        {isLoading ? (
          <div className="text-center text-gray-400 py-20">Loading farms...</div>
        ) : farms.length === 0 ? (
          <div className="text-center text-gray-400 py-20">
            <p className="text-xl mb-4">No farms yet</p>
            <p>Click "Add Farm" to get started</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {farms.map((farm: Farm) => (
              <div
                key={farm.id}
                className="bg-gray-900 border border-gray-800 rounded-xl p-6 hover:border-emerald-500 transition-all cursor-pointer group"
                onClick={() => window.location.href = `/farms/${farm.id}`}
              >
                {/* Health Indicator */}
                <div className="flex justify-between items-start mb-4">
                  <div className={`w-3 h-3 rounded-full ${getHealthColor(farm.health_score)}`} />
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      if (confirm(`Delete ${farm.name}?`)) {
                        deleteFarm.mutate(farm.id);
                      }
                    }}
                    className="opacity-0 group-hover:opacity-100 text-red-400 hover:text-red-300 transition-opacity"
                  >
                    <Trash2 size={18} />
                  </button>
                </div>

                {/* Farm Details */}
                <h3 className="text-xl font-semibold mb-2">{farm.name}</h3>
                <p className="text-emerald-400 text-sm uppercase tracking-wide mb-4">
                  {farm.crop_type}
                </p>

                <div className="space-y-2 text-sm text-gray-400">
                  <div className="flex items-center gap-2">
                    <MapPin size={16} />
                    <span>{farm.latitude.toFixed(4)}, {farm.longitude.toFixed(4)}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <TrendingUp size={16} />
                    <span>{farm.area} hectares</span>
                  </div>
                </div>

                {farm.health_score !== undefined && (
                  <div className="mt-4 pt-4 border-t border-gray-800">
                    <div className="flex justify-between items-center">
                      <span className="text-gray-400 text-sm">Health Score</span>
                      <span className="text-lg font-bold">{farm.health_score}%</span>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Add Farm Modal */}
        {isAddModalOpen && (
          <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-8 max-w-md w-full">
              <h2 className="text-2xl font-bold mb-6">Add New Farm</h2>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm text-gray-400 mb-2">Farm Name</label>
                  <input
                    type="text"
                    required
                    value={newFarm.name}
                    onChange={(e) => setNewFarm({ ...newFarm, name: e.target.value })}
                    className="w-full bg-black border border-gray-700 rounded-lg px-4 py-2 focus:outline-none focus:border-emerald-500"
                    placeholder="Green Valley Farm"
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-2">Crop Type</label>
                  <input
                    type="text"
                    required
                    value={newFarm.crop_type}
                    onChange={(e) => setNewFarm({ ...newFarm, crop_type: e.target.value })}
                    className="w-full bg-black border border-gray-700 rounded-lg px-4 py-2 focus:outline-none focus:border-emerald-500"
                    placeholder="wheat, rice, cotton..."
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm text-gray-400 mb-2">Latitude</label>
                    <input
                      type="number"
                      step="any"
                      required
                      value={newFarm.latitude}
                      onChange={(e) => setNewFarm({ ...newFarm, latitude: e.target.value })}
                      className="w-full bg-black border border-gray-700 rounded-lg px-4 py-2 focus:outline-none focus:border-emerald-500"
                      placeholder="28.6139"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-400 mb-2">Longitude</label>
                    <input
                      type="number"
                      step="any"
                      required
                      value={newFarm.longitude}
                      onChange={(e) => setNewFarm({ ...newFarm, longitude: e.target.value })}
                      className="w-full bg-black border border-gray-700 rounded-lg px-4 py-2 focus:outline-none focus:border-emerald-500"
                      placeholder="77.2090"
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-2">Area (hectares)</label>
                  <input
                    type="number"
                    step="any"
                    required
                    value={newFarm.area}
                    onChange={(e) => setNewFarm({ ...newFarm, area: e.target.value })}
                    className="w-full bg-black border border-gray-700 rounded-lg px-4 py-2 focus:outline-none focus:border-emerald-500"
                    placeholder="5.5"
                  />
                </div>
                <div className="flex gap-4 pt-4">
                  <button
                    type="button"
                    onClick={() => {
                      setIsAddModalOpen(false);
                      setNewFarm({ name: '', crop_type: '', latitude: '', longitude: '', area: '' });
                    }}
                    className="flex-1 bg-gray-800 hover:bg-gray-700 px-6 py-3 rounded-lg transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={createFarm.isPending}
                    className="flex-1 bg-emerald-600 hover:bg-emerald-700 px-6 py-3 rounded-lg transition-colors disabled:opacity-50"
                  >
                    {createFarm.isPending ? 'Creating...' : 'Create Farm'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
