'use client'

import { useState } from 'react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { User, Bell, Globe, Key, Save } from 'lucide-react'
import toast from 'react-hot-toast'

export default function SettingsPage() {
  const [profile, setProfile] = useState({
    name: 'John Doe',
    email: 'john@example.com',
    phone: '+1234567890',
  })

  const [notifications, setNotifications] = useState({
    emailAlerts: true,
    smsAlerts: false,
    pushAlerts: true,
    weeklyReports: true,
  })

  const [preferences, setPreferences] = useState({
    units: 'metric',
    dateFormat: 'DD/MM/YYYY',
    language: 'en',
    theme: 'dark',
  })

  const handleSaveProfile = () => {
    toast.success('Profile updated successfully!')
  }

  const handleSaveNotifications = () => {
    toast.success('Notification preferences saved!')
  }

  const handleSavePreferences = () => {
    toast.success('Preferences saved!')
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Settings</h1>
        <p className="text-gray-400">Manage your account and preferences</p>
      </div>

      <Tabs defaultValue="profile" className="space-y-6">
        <TabsList className="bg-zinc-900 border border-white/10">
          <TabsTrigger value="profile" className="data-[state=active]:bg-emerald-600 data-[state=active]:text-white">
            <User className="mr-2 h-4 w-4" />
            Profile
          </TabsTrigger>
          <TabsTrigger value="notifications" className="data-[state=active]:bg-emerald-600 data-[state=active]:text-white">
            <Bell className="mr-2 h-4 w-4" />
            Notifications
          </TabsTrigger>
          <TabsTrigger value="preferences" className="data-[state=active]:bg-emerald-600 data-[state=active]:text-white">
            <Globe className="mr-2 h-4 w-4" />
            Preferences
          </TabsTrigger>
          <TabsTrigger value="api" className="data-[state=active]:bg-emerald-600 data-[state=active]:text-white">
            <Key className="mr-2 h-4 w-4" />
            API Keys
          </TabsTrigger>
        </TabsList>

        <TabsContent value="profile">
          <Card className="bg-zinc-900 border-white/10 p-6">
            <div className="space-y-6">
              <div className="flex items-center gap-6">
                <Avatar className="h-24 w-24">
                  <AvatarImage src="" />
                  <AvatarFallback className="bg-emerald-600 text-white text-2xl">
                    JD
                  </AvatarFallback>
                </Avatar>
                <div>
                  <Button variant="outline" className="border-white/20 text-white hover:bg-white/5 mb-2">
                    Upload Photo
                  </Button>
                  <p className="text-sm text-gray-400">JPG, PNG or GIF. Max 2MB.</p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="name" className="text-white">Full Name</Label>
                  <Input
                    id="name"
                    value={profile.name}
                    onChange={(e) => setProfile({ ...profile, name: e.target.value })}
                    className="bg-black border-white/20 text-white"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="email" className="text-white">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    value={profile.email}
                    onChange={(e) => setProfile({ ...profile, email: e.target.value })}
                    className="bg-black border-white/20 text-white"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="phone" className="text-white">Phone</Label>
                  <Input
                    id="phone"
                    value={profile.phone}
                    onChange={(e) => setProfile({ ...profile, phone: e.target.value })}
                    className="bg-black border-white/20 text-white"
                  />
                </div>
              </div>

              <Button onClick={handleSaveProfile} className="bg-emerald-600 hover:bg-emerald-700 text-white">
                <Save className="mr-2 h-4 w-4" />
                Save Changes
              </Button>
            </div>
          </Card>
        </TabsContent>

        <TabsContent value="notifications">
          <Card className="bg-zinc-900 border-white/10 p-6">
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-white">Email Notifications</h3>
                  <p className="text-sm text-gray-400">Receive alerts via email</p>
                </div>
                <input
                  type="checkbox"
                  checked={notifications.emailAlerts}
                  onChange={(e) => setNotifications({ ...notifications, emailAlerts: e.target.checked })}
                  className="h-5 w-5 rounded border-white/20 bg-black text-emerald-600"
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-white">SMS Alerts</h3>
                  <p className="text-sm text-gray-400">Get text messages for critical issues</p>
                </div>
                <input
                  type="checkbox"
                  checked={notifications.smsAlerts}
                  onChange={(e) => setNotifications({ ...notifications, smsAlerts: e.target.checked })}
                  className="h-5 w-5 rounded border-white/20 bg-black text-emerald-600"
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-white">Push Notifications</h3>
                  <p className="text-sm text-gray-400">Browser push notifications</p>
                </div>
                <input
                  type="checkbox"
                  checked={notifications.pushAlerts}
                  onChange={(e) => setNotifications({ ...notifications, pushAlerts: e.target.checked })}
                  className="h-5 w-5 rounded border-white/20 bg-black text-emerald-600"
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-white">Weekly Reports</h3>
                  <p className="text-sm text-gray-400">Get a summary every week</p>
                </div>
                <input
                  type="checkbox"
                  checked={notifications.weeklyReports}
                  onChange={(e) => setNotifications({ ...notifications, weeklyReports: e.target.checked })}
                  className="h-5 w-5 rounded border-white/20 bg-black text-emerald-600"
                />
              </div>

              <Button onClick={handleSaveNotifications} className="bg-emerald-600 hover:bg-emerald-700 text-white">
                <Save className="mr-2 h-4 w-4" />
                Save Preferences
              </Button>
            </div>
          </Card>
        </TabsContent>

        <TabsContent value="preferences">
          <Card className="bg-zinc-900 border-white/10 p-6">
            <div className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="units" className="text-white">Units</Label>
                <select
                  id="units"
                  value={preferences.units}
                  onChange={(e) => setPreferences({ ...preferences, units: e.target.value })}
                  className="w-full p-2 rounded-lg bg-black border border-white/20 text-white"
                >
                  <option value="metric">Metric (hectares, °C)</option>
                  <option value="imperial">Imperial (acres, °F)</option>
                </select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="dateFormat" className="text-white">Date Format</Label>
                <select
                  id="dateFormat"
                  value={preferences.dateFormat}
                  onChange={(e) => setPreferences({ ...preferences, dateFormat: e.target.value })}
                  className="w-full p-2 rounded-lg bg-black border border-white/20 text-white"
                >
                  <option value="DD/MM/YYYY">DD/MM/YYYY</option>
                  <option value="MM/DD/YYYY">MM/DD/YYYY</option>
                  <option value="YYYY-MM-DD">YYYY-MM-DD</option>
                </select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="language" className="text-white">Language</Label>
                <select
                  id="language"
                  value={preferences.language}
                  onChange={(e) => setPreferences({ ...preferences, language: e.target.value })}
                  className="w-full p-2 rounded-lg bg-black border border-white/20 text-white"
                >
                  <option value="en">English</option>
                  <option value="es">Spanish</option>
                  <option value="fr">French</option>
                  <option value="hi">Hindi</option>
                </select>
              </div>

              <Button onClick={handleSavePreferences} className="bg-emerald-600 hover:bg-emerald-700 text-white">
                <Save className="mr-2 h-4 w-4" />
                Save Preferences
              </Button>
            </div>
          </Card>
        </TabsContent>

        <TabsContent value="api">
          <Card className="bg-zinc-900 border-white/10 p-6">
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-white mb-2">API Key</h3>
                <p className="text-sm text-gray-400 mb-4">Use this key to access the AgroVision API</p>
                <div className="flex gap-2">
                  <Input
                    value="sk_test_xxxxxxxxxxxxxxxxxxxxx"
                    readOnly
                    className="bg-black border-white/20 text-white font-mono"
                  />
                  <Button variant="outline" className="border-white/20 text-white hover:bg-white/5">
                    Copy
                  </Button>
                </div>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-white mb-2">Usage Statistics</h3>
                <div className="grid grid-cols-3 gap-4">
                  <div className="p-4 rounded-lg bg-black/50 border border-white/10">
                    <p className="text-sm text-gray-400">Requests This Month</p>
                    <p className="text-2xl font-bold text-white">1,234</p>
                  </div>
                  <div className="p-4 rounded-lg bg-black/50 border border-white/10">
                    <p className="text-sm text-gray-400">Limit</p>
                    <p className="text-2xl font-bold text-white">10,000</p>
                  </div>
                  <div className="p-4 rounded-lg bg-black/50 border border-white/10">
                    <p className="text-sm text-gray-400">Remaining</p>
                    <p className="text-2xl font-bold text-emerald-500">8,766</p>
                  </div>
                </div>
              </div>

              <Button variant="destructive" className="bg-red-600 hover:bg-red-700 text-white">
                Regenerate API Key
              </Button>
            </div>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
