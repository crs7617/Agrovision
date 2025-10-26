'use client'

import { useEffect, useState } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
  LayoutDashboard,
  Sprout,
  BarChart3,
  MessageSquare,
  Settings,
  Bell,
  Menu,
  X,
  LogOut,
} from 'lucide-react'
import { getCurrentUser, signOut } from '@/lib/supabase/client'
import toast from 'react-hot-toast'
import type { User as UserType } from '@/types'
import { ErrorBoundary } from '@/components/ErrorBoundary'

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const router = useRouter()
  const pathname = usePathname()
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [user, setUser] = useState<UserType | null>(null)

  useEffect(() => {
    const checkAuth = async () => {
      const currentUser = await getCurrentUser()
      if (!currentUser) {
        router.push('/login')
      } else {
        setUser(currentUser as UserType)
      }
    }
    checkAuth()
  }, [router])

  const handleSignOut = async () => {
    await signOut()
    toast.success('Signed out successfully')
    router.push('/login')
  }

  const navItems = [
    { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { href: '/farms', label: 'Farms', icon: Sprout },
    { href: '/analysis', label: 'Analysis', icon: BarChart3 },
    { href: '/chat', label: 'AI Chat', icon: MessageSquare },
    { href: '/settings', label: 'Settings', icon: Settings },
  ]

  return (
    <div className="min-h-screen bg-black">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed top-0 left-0 z-50 h-full w-64 bg-zinc-900 border-r border-white/10 transition-transform duration-300 lg:translate-x-0 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center gap-2 px-6 py-5 border-b border-white/10">
            <Sprout className="h-8 w-8 text-emerald-500" />
            <span className="text-xl font-bold text-white">AgroVision</span>
            <button
              onClick={() => setSidebarOpen(false)}
              className="ml-auto lg:hidden text-gray-400 hover:text-white"
            >
              <X className="h-6 w-6" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-2">
            {navItems.map((item) => {
              const isActive = pathname === item.href
              const Icon = item.icon
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                    isActive
                      ? 'bg-emerald-600 text-white'
                      : 'text-gray-400 hover:bg-white/5 hover:text-white'
                  }`}
                >
                  <Icon className="h-5 w-5" />
                  <span className="font-medium">{item.label}</span>
                </Link>
              )
            })}
          </nav>

          {/* User section */}
          <div className="p-4 border-t border-white/10">
            <div className="flex items-center gap-3 px-4 py-3 rounded-lg bg-white/5">
              <Avatar className="h-10 w-10">
                <AvatarImage src={user?.user_metadata?.avatar_url} />
                <AvatarFallback className="bg-emerald-600 text-white">
                  {user?.user_metadata?.name?.[0] || user?.email?.[0]?.toUpperCase() || 'U'}
                </AvatarFallback>
              </Avatar>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-white truncate">
                  {user?.user_metadata?.name || user?.email || 'User'}
                </p>
                <p className="text-xs text-gray-400 truncate">{user?.email}</p>
              </div>
            </div>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Top navbar */}
        <header className="sticky top-0 z-30 bg-black/80 backdrop-blur-xl border-b border-white/10">
          <div className="flex items-center justify-between px-6 py-4">
            <button
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden text-white"
            >
              <Menu className="h-6 w-6" />
            </button>

            <div className="ml-auto flex items-center gap-4">
              {/* Notifications */}
              <Button variant="ghost" size="icon" className="text-white hover:text-emerald-500">
                <Bell className="h-5 w-5" />
              </Button>

              {/* User dropdown */}
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="h-10 w-10 rounded-full p-0">
                    <Avatar className="h-10 w-10">
                      <AvatarImage src={user?.user_metadata?.avatar_url} />
                      <AvatarFallback className="bg-emerald-600 text-white">
                        {user?.user_metadata?.name?.[0] || user?.email?.[0]?.toUpperCase() || 'U'}
                      </AvatarFallback>
                    </Avatar>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-56 bg-zinc-900 border-white/10">
                  <DropdownMenuLabel className="text-white">My Account</DropdownMenuLabel>
                  <DropdownMenuSeparator className="bg-white/10" />
                  <DropdownMenuItem className="text-gray-300 hover:text-white hover:bg-white/5" asChild>
                    <Link href="/settings">
                      <Settings className="mr-2 h-4 w-4" />
                      Profile
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem className="text-gray-300 hover:text-white hover:bg-white/5" asChild>
                    <Link href="/settings">
                      <Settings className="mr-2 h-4 w-4" />
                      Settings
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuSeparator className="bg-white/10" />
                  <DropdownMenuItem
                    className="text-red-400 hover:text-red-300 hover:bg-white/5 cursor-pointer"
                    onClick={handleSignOut}
                  >
                    <LogOut className="mr-2 h-4 w-4" />
                    Sign Out
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="p-6">
          <ErrorBoundary>{children}</ErrorBoundary>
        </main>
      </div>
    </div>
  )
}
