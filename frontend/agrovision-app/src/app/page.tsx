import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Sprout, BarChart3, MessageSquare, MapIcon, ArrowRight } from 'lucide-react';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      {/* Navigation */}
      <nav className="border-b border-slate-800 backdrop-blur-sm bg-slate-950/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <Sprout className="h-8 w-8 text-emerald-500" />
              <span className="text-2xl font-bold bg-gradient-to-r from-emerald-400 to-blue-500 bg-clip-text text-transparent">
                AgroVision
              </span>
            </div>
            <div className="flex gap-4">
              <Link href="/login">
                <Button variant="ghost">Log in</Button>
              </Link>
              <Link href="/signup">
                <Button className="bg-emerald-600 hover:bg-emerald-700">
                  Get Started
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-emerald-500/10 via-transparent to-transparent"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 text-center">
          <h1 className="text-5xl md:text-7xl font-bold mb-6">
            <span className="bg-gradient-to-r from-emerald-400 via-blue-500 to-emerald-400 bg-clip-text text-transparent">
              AI-Powered Crop Monitoring
            </span>
          </h1>
          <p className="text-xl text-slate-400 max-w-3xl mx-auto mb-12">
            Harness satellite imagery and machine learning to optimize your farm&apos;s health, 
            predict yields, and make data-driven decisions for sustainable agriculture.
          </p>
          <Link href="/dashboard">
            <Button size="lg" className="bg-emerald-600 hover:bg-emerald-700 text-lg px-8 py-6">
              Launch Dashboard
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
          </Link>
        </div>
      </div>

      {/* Features Grid */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card className="bg-slate-900 border-slate-800 p-6 hover:border-emerald-500/50 transition-all group">
            <div className="w-12 h-12 bg-emerald-500/10 rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
              <Sprout className="h-6 w-6 text-emerald-500" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Farm Management</h3>
            <p className="text-slate-400 text-sm">
              Monitor multiple farms with real-time health tracking and comprehensive crop analysis
            </p>
          </Card>

          <Card className="bg-slate-900 border-slate-800 p-6 hover:border-blue-500/50 transition-all group">
            <div className="w-12 h-12 bg-blue-500/10 rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
              <BarChart3 className="h-6 w-6 text-blue-500" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Satellite Analysis</h3>
            <p className="text-slate-400 text-sm">
              Advanced NDVI, EVI, and SAVI metrics from high-resolution Sentinel-2 imagery
            </p>
          </Card>

          <Card className="bg-slate-900 border-slate-800 p-6 hover:border-purple-500/50 transition-all group">
            <div className="w-12 h-12 bg-purple-500/10 rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
              <MessageSquare className="h-6 w-6 text-purple-500" />
            </div>
            <h3 className="text-lg font-semibold mb-2">AI Assistant</h3>
            <p className="text-slate-400 text-sm">
              Get instant recommendations and insights from our intelligent farming chatbot
            </p>
          </Card>

          <Card className="bg-slate-900 border-slate-800 p-6 hover:border-yellow-500/50 transition-all group">
            <div className="w-12 h-12 bg-yellow-500/10 rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
              <MapIcon className="h-6 w-6 text-yellow-500" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Interactive Maps</h3>
            <p className="text-slate-400 text-sm">
              Visualize farm boundaries, health zones, and satellite imagery on detailed maps
            </p>
          </Card>
        </div>
      </div>

      {/* Stats Section */}
      <div className="border-t border-slate-800 bg-slate-900/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
            <div>
              <div className="text-4xl font-bold text-emerald-500 mb-2">95%</div>
              <div className="text-slate-400">Prediction Accuracy</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-blue-500 mb-2">Real-time</div>
              <div className="text-slate-400">Satellite Monitoring</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-purple-500 mb-2">24/7</div>
              <div className="text-slate-400">AI Support</div>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <p className="text-center text-slate-500 text-sm">
            © 2025 AgroVision. Empowering farmers with AI and satellite technology.
          </p>
        </div>
      </footer>
    </div>
  );
}
