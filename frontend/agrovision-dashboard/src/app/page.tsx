import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  Satellite, 
  Leaf, 
  BarChart3, 
  Activity, 
  Database, 
  Brain, 
  Layers, 
  MapPin,
  TrendingUp,
  Zap,
  Settings,
  Menu
} from "lucide-react";

export default function AgroVisionDashboard() {
  return (
    <div className="min-h-screen bg-dashboard text-white">
      {/* Header */}
      <header className="border-b border-white/10 bg-black/50 backdrop-blur-xl">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-purple-600 rounded-lg flex items-center justify-center">
                <Satellite className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="sidebar-brand">AgroVision</h1>
                <p className="text-xs text-gray-400">Agricultural Intelligence Platform</p>
              </div>
            </div>
            
            <nav className="hidden md:flex items-center space-x-8">
              <a href="#" className="nav-accent px-4 py-2 rounded-lg text-sm font-medium">Dashboard</a>
              <a href="#" className="nav-accent px-4 py-2 rounded-lg text-sm font-medium text-gray-400 hover:text-white">Analytics</a>
              <a href="#" className="nav-accent px-4 py-2 rounded-lg text-sm font-medium text-gray-400 hover:text-white">Monitoring</a>
              <a href="#" className="nav-accent px-4 py-2 rounded-lg text-sm font-medium text-gray-400 hover:text-white">Reports</a>
            </nav>

            <div className="flex items-center space-x-4">
              <Button variant="ghost" size="sm">
                <Settings className="w-4 h-4" />
              </Button>
              <Button variant="ghost" size="sm" className="md:hidden">
                <Menu className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        {/* Status Bar */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-semibold text-gradient-primary">System Overview</h2>
            <div className="flex items-center space-x-4 text-sm">
              <div className="flex items-center">
                <span className="status-indicator status-online"></span>
                <span className="text-gray-300">Data Processing Active</span>
              </div>
              <div className="flex items-center">
                <span className="status-indicator status-online"></span>
                <span className="text-gray-300">Satellite Connection</span>
              </div>
              <div className="flex items-center">
                <span className="status-indicator status-warning"></span>
                <span className="text-gray-300">Analysis Queue: 3</span>
              </div>
            </div>
          </div>
        </div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="metric-card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-400">Images Processed</p>
                <p className="text-2xl font-bold text-gradient-primary">2,847</p>
                <p className="text-xs text-green-400 flex items-center mt-1">
                  <TrendingUp className="w-3 h-3 mr-1" />
                  +12% this week
                </p>
              </div>
              <div className="w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center">
                <Database className="w-6 h-6 text-green-400" />
              </div>
            </div>
          </Card>

          <Card className="metric-card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-400">Active Sensors</p>
                <p className="text-2xl font-bold text-gradient-primary">156</p>
                <p className="text-xs text-green-400 flex items-center mt-1">
                  <Activity className="w-3 h-3 mr-1" />
                  All operational
                </p>
              </div>
              <div className="w-12 h-12 bg-purple-500/20 rounded-lg flex items-center justify-center">
                <Satellite className="w-6 h-6 text-purple-400" />
              </div>
            </div>
          </Card>

          <Card className="metric-card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-400">Analysis Accuracy</p>
                <p className="text-2xl font-bold text-gradient-primary">97.3%</p>
                <p className="text-xs text-green-400 flex items-center mt-1">
                  <BarChart3 className="w-3 h-3 mr-1" />
                  +2.1% improvement
                </p>
              </div>
              <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center">
                <Brain className="w-6 h-6 text-blue-400" />
              </div>
            </div>
          </Card>

          <Card className="metric-card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-400">Coverage Area</p>
                <p className="text-2xl font-bold text-gradient-primary">15.2K</p>
                <p className="text-xs text-gray-400 mt-1">hectares monitored</p>
              </div>
              <div className="w-12 h-12 bg-emerald-500/20 rounded-lg flex items-center justify-center">
                <MapPin className="w-6 h-6 text-emerald-400" />
              </div>
            </div>
          </Card>
        </div>

        {/* Main Dashboard Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Primary Analysis Panel */}
          <div className="lg:col-span-2">
            <Card className="card-glass">
              <CardHeader>
                <CardTitle className="text-xl font-semibold text-white flex items-center">
                  <Layers className="w-5 h-5 mr-2 text-green-400" />
                  Multispectral Analysis Pipeline
                </CardTitle>
                <CardDescription className="text-gray-400">
                  Real-time satellite data processing and vegetation index calculation
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="chart-container p-4 rounded-lg">
                    <h4 className="text-sm font-medium text-gray-300 mb-3">NDVI Distribution</h4>
                    <div className="h-32 bg-gradient-to-r from-green-500/20 to-green-600/40 rounded flex items-end justify-center">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-green-400">0.847</div>
                        <div className="text-xs text-gray-400">Average Index</div>
                      </div>
                    </div>
                  </div>
                  <div className="chart-container p-4 rounded-lg">
                    <h4 className="text-sm font-medium text-gray-300 mb-3">Processing Queue</h4>
                    <div className="h-32 bg-gradient-to-r from-purple-500/20 to-purple-600/40 rounded flex items-end justify-center">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-purple-400">3</div>
                        <div className="text-xs text-gray-400">Pending Tasks</div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <Leaf className="w-5 h-5 text-green-400" />
                      <span className="text-sm font-medium">Crop Health Assessment</span>
                    </div>
                    <Badge className="bg-green-500/20 text-green-400 border-green-500/30">Active</Badge>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <Satellite className="w-5 h-5 text-blue-400" />
                      <span className="text-sm font-medium">Sentinel-2 Data Sync</span>
                    </div>
                    <Badge className="bg-blue-500/20 text-blue-400 border-blue-500/30">Processing</Badge>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <Brain className="w-5 h-5 text-purple-400" />
                      <span className="text-sm font-medium">ML Model Training</span>
                    </div>
                    <Badge className="bg-gray-500/20 text-gray-400 border-gray-500/30">Queued</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Sidebar Information */}
          <div className="space-y-6">
            <Card className="card-elevated">
              <CardHeader>
                <CardTitle className="text-lg font-semibold text-white">System Performance</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-400">CPU Usage</span>
                    <span className="text-white">67%</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div className="bg-gradient-to-r from-green-400 to-green-500 h-2 rounded-full" style={{width: '67%'}}></div>
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-400">Memory</span>
                    <span className="text-white">82%</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div className="bg-gradient-to-r from-purple-400 to-purple-500 h-2 rounded-full" style={{width: '82%'}}></div>
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-400">Storage</span>
                    <span className="text-white">45%</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div className="bg-gradient-to-r from-blue-400 to-blue-500 h-2 rounded-full" style={{width: '45%'}}></div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="card-elevated">
              <CardHeader>
                <CardTitle className="text-lg font-semibold text-white">Recent Activity</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-start space-x-3">
                  <div className="w-2 h-2 bg-green-400 rounded-full mt-2"></div>
                  <div>
                    <p className="text-sm text-white">NDVI analysis completed</p>
                    <p className="text-xs text-gray-400">2 minutes ago</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="w-2 h-2 bg-blue-400 rounded-full mt-2"></div>
                  <div>
                    <p className="text-sm text-white">New satellite data received</p>
                    <p className="text-xs text-gray-400">15 minutes ago</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="w-2 h-2 bg-purple-400 rounded-full mt-2"></div>
                  <div>
                    <p className="text-sm text-white">Model accuracy improved</p>
                    <p className="text-xs text-gray-400">1 hour ago</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="w-2 h-2 bg-yellow-400 rounded-full mt-2"></div>
                  <div>
                    <p className="text-sm text-white">Processing queue cleared</p>
                    <p className="text-xs text-gray-400">3 hours ago</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Technology Stack */}
        <Card className="card-glass">
          <CardHeader>
            <CardTitle className="text-xl font-semibold text-white flex items-center">
              <Zap className="w-5 h-5 mr-2 text-purple-400" />
              Technology Stack
            </CardTitle>
            <CardDescription className="text-gray-400">
              Core technologies powering the AgroVision platform
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-4 bg-white/5 rounded-lg">
                <div className="text-sm font-medium text-green-400 mb-2">Data Processing</div>
                <div className="space-y-1 text-xs text-gray-300">
                  <div>Python</div>
                  <div>NumPy</div>
                  <div>GDAL</div>
                </div>
              </div>
              <div className="text-center p-4 bg-white/5 rounded-lg">
                <div className="text-sm font-medium text-purple-400 mb-2">Machine Learning</div>
                <div className="space-y-1 text-xs text-gray-300">
                  <div>TensorFlow</div>
                  <div>Scikit-learn</div>
                  <div>OpenCV</div>
                </div>
              </div>
              <div className="text-center p-4 bg-white/5 rounded-lg">
                <div className="text-sm font-medium text-blue-400 mb-2">Satellite APIs</div>
                <div className="space-y-1 text-xs text-gray-300">
                  <div>Sentinel Hub</div>
                  <div>Copernicus</div>
                  <div>Google Earth</div>
                </div>
              </div>
              <div className="text-center p-4 bg-white/5 rounded-lg">
                <div className="text-sm font-medium text-emerald-400 mb-2">Frontend</div>
                <div className="space-y-1 text-xs text-gray-300">
                  <div>Next.js</div>
                  <div>TypeScript</div>
                  <div>Tailwind</div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
