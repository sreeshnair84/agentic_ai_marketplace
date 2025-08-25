'use client';

import { AuthGuard } from '@/components/auth/AuthGuard';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { StandardPageLayout, StandardSection, StandardGrid, StandardCard } from '@/components/layout/StandardPageLayout';
import { 
  Activity, 
  Bot, 
  Workflow, 
  MessageSquare, 
  TrendingUp,
  AlertCircle,
  CheckCircle,
  Clock,
  Zap,
  RefreshCw,
  Wifi,
  WifiOff
} from 'lucide-react';
import Link from 'next/link';
import { useDashboardData, useLiveMetrics, useSystemHealth } from '@/hooks/useDashboardData';
import { cn } from '@/lib/utils';

interface ServiceHealth {
  status: 'healthy' | 'unhealthy';
  response_time_ms?: number;
}

export default function DashboardPage() {
  const { data: dashboardData, loading, error, lastUpdated, refresh } = useDashboardData();
  const liveMetrics = useLiveMetrics();
  const systemHealth = useSystemHealth();

  // Fallback data for when API is not available
  const metrics = liveMetrics || {
    activeAgents: 0,
    runningWorkflows: 0,
    a2aMessages: 0,
    responseTime: 0,
    totalServices: 0,
    healthyServices: 0
  };

  const recentActivity = dashboardData?.recentActivity || [];

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    
    if (diffMs < 60000) {
      return 'Just now';
    } else if (diffMs < 3600000) {
      const minutes = Math.floor(diffMs / 60000);
      return `${minutes} minute${minutes !== 1 ? 's' : ''} ago`;
    } else if (diffMs < 86400000) {
      const hours = Math.floor(diffMs / 3600000);
      return `${hours} hour${hours !== 1 ? 's' : ''} ago`;
    } else {
      const days = Math.floor(diffMs / 86400000);
      return `${days} day${days !== 1 ? 's' : ''} ago`;
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'warning':
        return <AlertCircle className="h-4 w-4 text-yellow-500" />;
      case 'error':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      case 'running':
        return <Clock className="h-4 w-4 text-blue-500" />;
      default:
        return <Activity className="h-4 w-4 text-gray-500" />;
    }
  };

  const getActivityTypeIcon = (type: string) => {
    switch (type) {
      case 'agent':
        return <Bot className="h-4 w-4" />;
      case 'workflow':
        return <Workflow className="h-4 w-4" />;
      case 'a2a':
        return <MessageSquare className="h-4 w-4" />;
      case 'tool':
        return <Zap className="h-4 w-4" />;
      case 'service':
        return <Activity className="h-4 w-4" />;
      default:
        return <Activity className="h-4 w-4" />;
    }
  };

  return (
    <AuthGuard>
      <StandardPageLayout
        title="Platform Dashboard"
        description="Real-time insights into your multi-agent AI ecosystem with comprehensive performance monitoring and analytics"
        variant="adaptive"
        actions={
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3 sm:gap-4">
            {lastUpdated && (
              <span className="text-caption text-gray-500 flex items-center">
                <Clock className="h-4 w-4 mr-1 flex-shrink-0" />
                <span className="truncate">Updated {formatTimestamp(lastUpdated.toISOString())}</span>
              </span>
            )}
            <Button 
              variant="outline" 
              size="sm" 
              onClick={refresh}
              disabled={loading}
              className="flex items-center gap-2 w-full sm:w-auto"
            >
              <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
              <span>Refresh</span>
            </Button>
          </div>
        }
      >

        {/* Enhanced Error Banner */}
        {error && (
          <StandardSection>
            <StandardCard variant="outlined" className="border-red-300/50 bg-gradient-to-r from-red-50 to-red-100/50 dark:border-red-700/50 dark:from-red-900/20 dark:to-red-800/10">
              <div className="flex flex-col sm:flex-row sm:items-center gap-4">
                <div className="flex items-start gap-3 flex-1 min-w-0">
                  <div className="w-10 h-10 bg-red-100 dark:bg-red-900/30 rounded-xl flex items-center justify-center flex-shrink-0">
                    <AlertCircle className="h-5 w-5 text-red-600 dark:text-red-400" />
                  </div>
                  <div className="min-w-0">
                    <h3 className="text-lg font-semibold text-red-800 dark:text-red-200 mb-1">Connection Issue</h3>
                    <span className="text-red-700 dark:text-red-300 break-words">
                      Failed to fetch dashboard data: {error}
                    </span>
                  </div>
                </div>
                <Button variant="outline" size="sm" onClick={refresh} className="flex-shrink-0 border-red-300 text-red-700 hover:bg-red-50">
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Retry
                </Button>
              </div>
            </StandardCard>
          </StandardSection>
        )}

        {/* Enhanced System Health Banner */}
        <StandardSection>
          <StandardCard variant="elevated" className="bg-gradient-to-r from-blue-50 via-white to-purple-50/30 dark:from-gray-800/80 dark:via-gray-700/80 dark:to-gray-800/80 border-blue-200/30 dark:border-blue-700/30">
            <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
              <div className="flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-4 flex-1 min-w-0">
                <div className="flex items-center gap-2 sm:gap-3">
                  {loading ? (
                    <>
                      <RefreshCw className="h-5 w-5 sm:h-6 sm:w-6 text-blue-500 animate-spin flex-shrink-0" />
                      <span className="text-heading-3">Loading System Status...</span>
                    </>
                  ) : systemHealth ? (
                    <>
                      {systemHealth.status === 'healthy' ? (
                        <CheckCircle className="h-5 w-5 sm:h-6 sm:w-6 text-green-500 flex-shrink-0" />
                      ) : systemHealth.status === 'degraded' ? (
                        <AlertCircle className="h-5 w-5 sm:h-6 sm:w-6 text-yellow-500 flex-shrink-0" />
                      ) : (
                        <AlertCircle className="h-5 w-5 sm:h-6 sm:w-6 text-red-500 flex-shrink-0" />
                      )}
                      <span className="text-heading-3 truncate">
                        System {systemHealth.status === 'healthy' ? 'Healthy' : 
                                 systemHealth.status === 'degraded' ? 'Degraded' : 'Unhealthy'}
                      </span>
                    </>
                  ) : (
                    <>
                      <WifiOff className="h-5 w-5 sm:h-6 sm:w-6 text-gray-500 flex-shrink-0" />
                      <span className="text-heading-3">System Status Unknown</span>
                    </>
                  )}
                </div>
                {systemHealth && (
                  <Badge 
                    variant="outline" 
                    className={cn(
                      "flex-shrink-0",
                      systemHealth.status === 'healthy' 
                        ? "bg-green-50 text-green-700 border-green-200 dark:bg-green-900/20 dark:text-green-300 dark:border-green-800"
                        : systemHealth.status === 'degraded'
                        ? "bg-yellow-50 text-yellow-700 border-yellow-200 dark:bg-yellow-900/20 dark:text-yellow-300 dark:border-yellow-800"
                        : "bg-red-50 text-red-700 border-red-200 dark:bg-red-900/20 dark:text-red-300 dark:border-red-800"
                    )}
                  >
                    {systemHealth.servicesCount?.healthy || 0}/{systemHealth.servicesCount?.total || 0} Services Operational
                  </Badge>
                )}
              </div>
              <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4 text-caption text-gray-600 dark:text-gray-300">
                {systemHealth && (
                  <span className="flex items-center gap-1">
                    <span>Uptime: {systemHealth.uptime}</span>
                  </span>
                )}
                {dashboardData && (
                  <span className="flex items-center gap-1">
                    <Wifi className="h-3 w-3 sm:h-4 sm:w-4" />
                    <span>Live Data</span>
                  </span>
                )}
              </div>
            </div>
          </StandardCard>
        </StandardSection>

        {/* Enhanced Metrics Cards */}
        <StandardSection title="Key Performance Metrics" description="Real-time system performance indicators and statistics">
          <StandardGrid cols={{ default: 1, sm: 2, lg: 4, xl: 4, '2xl': 6 }} gap="lg">
            <StandardCard variant="elevated" className="group hover:scale-[1.02] transition-all duration-300 bg-gradient-to-br from-blue-50 to-blue-100/50 dark:from-blue-900/20 dark:to-blue-800/10 border-blue-200/30 dark:border-blue-700/30">
              <div className="flex flex-row items-center justify-between space-y-0 pb-4">
                <h3 className="text-sm font-semibold text-blue-800 dark:text-blue-200">Active Agents</h3>
                <div className="w-12 h-12 bg-blue-500 rounded-xl flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform">
                  <Bot className="h-6 w-6 text-white" />
                </div>
              </div>
              <div className="pt-0">
                <div className="text-4xl xl:text-5xl font-bold text-blue-900 dark:text-blue-100 mb-2">{metrics.activeAgents}</div>
                <div className="flex items-center gap-2">
                  <div className="flex items-center gap-1 px-2 py-1 bg-blue-100/80 dark:bg-blue-800/30 rounded-lg">
                    <TrendingUp className="h-3 w-3 text-blue-600 dark:text-blue-400 flex-shrink-0" />
                    <span className="text-xs font-medium text-blue-700 dark:text-blue-300 truncate">
                      {metrics.healthyServices > 0 ? 'Online' : 'Waiting'}
                    </span>
                  </div>
                </div>
              </div>
            </StandardCard>

            <StandardCard variant="elevated" className="group hover:scale-[1.02] transition-all duration-300 bg-gradient-to-br from-green-50 to-green-100/50 dark:from-green-900/20 dark:to-green-800/10 border-green-200/30 dark:border-green-700/30">
              <div className="flex flex-row items-center justify-between space-y-0 pb-4">
                <h3 className="text-sm font-semibold text-green-800 dark:text-green-200">Running Workflows</h3>
                <div className="w-12 h-12 bg-green-500 rounded-xl flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform">
                  <Workflow className="h-6 w-6 text-white" />
                </div>
              </div>
              <div className="pt-0">
                <div className="text-4xl xl:text-5xl font-bold text-green-900 dark:text-green-100 mb-2">{metrics.runningWorkflows}</div>
                <div className="flex items-center gap-2">
                  <div className="flex items-center gap-1 px-2 py-1 bg-green-100/80 dark:bg-green-800/30 rounded-lg">
                    <Activity className="h-3 w-3 text-green-600 dark:text-green-400 flex-shrink-0" />
                    <span className="text-xs font-medium text-green-700 dark:text-green-300 truncate">
                      {metrics.runningWorkflows > 0 ? 'Active' : 'Idle'}
                    </span>
                  </div>
                </div>
              </div>
            </StandardCard>

            <StandardCard variant="elevated" className="group hover:scale-[1.02] transition-all duration-300 bg-gradient-to-br from-purple-50 to-purple-100/50 dark:from-purple-900/20 dark:to-purple-800/10 border-purple-200/30 dark:border-purple-700/30">
              <div className="flex flex-row items-center justify-between space-y-0 pb-4">
                <h3 className="text-sm font-semibold text-purple-800 dark:text-purple-200">A2A Messages</h3>
                <div className="w-12 h-12 bg-purple-500 rounded-xl flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform">
                  <MessageSquare className="h-6 w-6 text-white" />
                </div>
              </div>
              <div className="pt-0">
                <div className="text-4xl xl:text-5xl font-bold text-purple-900 dark:text-purple-100 mb-2">{metrics.a2aMessages}</div>
                <div className="flex items-center gap-2">
                  <div className="flex items-center gap-1 px-2 py-1 bg-purple-100/80 dark:bg-purple-800/30 rounded-lg">
                    <TrendingUp className="h-3 w-3 text-purple-600 dark:text-purple-400 flex-shrink-0" />
                    <span className="text-xs font-medium text-purple-700 dark:text-purple-300 truncate">
                      {dashboardData ? 'Live' : 'Static'}
                    </span>
                  </div>
                </div>
              </div>
            </StandardCard>

            <StandardCard variant="elevated" className="group hover:scale-[1.02] transition-all duration-300 bg-gradient-to-br from-yellow-50 to-yellow-100/50 dark:from-yellow-900/20 dark:to-yellow-800/10 border-yellow-200/30 dark:border-yellow-700/30">
              <div className="flex flex-row items-center justify-between space-y-0 pb-4">
                <h3 className="text-sm font-semibold text-yellow-800 dark:text-yellow-200">Response Time</h3>
                <div className="w-12 h-12 bg-yellow-500 rounded-xl flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform">
                  <Zap className="h-6 w-6 text-white" />
                </div>
              </div>
              <div className="pt-0">
                <div className="text-4xl xl:text-5xl font-bold text-yellow-900 dark:text-yellow-100 mb-2">
                  {metrics.responseTime > 0 ? `${Math.round(metrics.responseTime)}ms` : 'N/A'}
                </div>
                <div className="flex items-center gap-2">
                  <div className="flex items-center gap-1 px-2 py-1 bg-yellow-100/80 dark:bg-yellow-800/30 rounded-lg">
                    <TrendingUp className="h-3 w-3 text-yellow-600 dark:text-yellow-400 flex-shrink-0" />
                    <span className="text-xs font-medium text-yellow-700 dark:text-yellow-300 truncate">
                      {metrics.healthyServices}/{metrics.totalServices} Services
                    </span>
                  </div>
                </div>
              </div>
            </StandardCard>
          </StandardGrid>
        </StandardSection>

        <StandardSection title="Activity & Management" description="Recent system activity and quick management tools">
          <StandardGrid cols={{ default: 1, xl: 3, '2xl': 4 }} gap="xl">
            {/* Enhanced Recent Activity */}
            <div className="xl:col-span-2 2xl:col-span-3">
              <StandardCard variant="elevated" 
                title="Recent Activity" 
                description="Live feed of system events and agent interactions"
                actions={
                  <Button variant="outline" size="sm" asChild className="flex-shrink-0">
                    <Link href="/observability">
                      <Activity className="h-4 w-4 mr-2" />
                      View All
                    </Link>
                  </Button>
                }>
                {loading ? (
                  <div className="flex items-center justify-center p-8">
                    <RefreshCw className="h-6 w-6 animate-spin text-gray-400" />
                    <span className="ml-2 text-gray-500">Loading activity...</span>
                  </div>
                ) : recentActivity.length > 0 ? (
                  <div className="space-y-3">
                    {recentActivity.map((activity) => (
                      <div key={activity.id} className="flex items-start gap-4 p-4 rounded-xl hover:bg-gradient-to-r hover:from-gray-50 hover:to-blue-50/30 dark:hover:from-gray-800/50 dark:hover:to-gray-700/50 transition-all duration-200 border border-gray-100 dark:border-gray-700/50 hover:border-blue-200 dark:hover:border-blue-700/50 hover:shadow-sm">
                        <div className="flex-shrink-0">
                          <div className="flex items-center justify-center w-12 h-12 rounded-xl bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-700 dark:to-gray-800 shadow-sm">
                            {getActivityTypeIcon(activity.type)}
                          </div>
                        </div>
                        <div className="flex-grow min-w-0">
                          <div className="flex items-center gap-2 mb-2">
                            <h4 className="font-semibold text-gray-900 dark:text-white truncate">
                              {activity.title}
                            </h4>
                            <div className="flex-shrink-0">
                              {getStatusIcon(activity.status)}
                            </div>
                          </div>
                          <p className="text-gray-600 dark:text-gray-300 line-clamp-2 leading-relaxed mb-2">
                            {activity.description}
                          </p>
                          <div className="flex items-center gap-2">
                            <Clock className="h-3 w-3 text-gray-400 flex-shrink-0" />
                            <p className="text-xs font-medium text-gray-500 dark:text-gray-400">
                              {formatTimestamp(activity.timestamp)}
                            </p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    <div className="flex flex-col items-center">
                      <Activity className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                      <p className="text-body-sm mb-2">No recent activity available</p>
                      <Button variant="outline" size="sm" onClick={refresh}>
                        Refresh
                      </Button>
                    </div>
                  </div>
                )}
              </StandardCard>
            </div>

            {/* Enhanced Sidebar */}
            <div className="space-y-8">
              {/* Enhanced Quick Actions */}
              <StandardCard variant="elevated" title="Quick Actions" description="Common tasks and operations">
                <div className="space-y-4">
                  <Button className="w-full justify-start h-12 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white shadow-lg hover:shadow-xl transition-all duration-200" asChild>
                    <Link href="/agents" className="flex items-center gap-4">
                      <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
                        <Bot className="h-5 w-5" />
                      </div>
                      <span className="font-semibold">Create Agent</span>
                    </Link>
                  </Button>
                  <Button className="w-full justify-start h-12 bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white shadow-lg hover:shadow-xl transition-all duration-200" variant="outline" asChild>
                    <Link href="/workflows" className="flex items-center gap-4">
                      <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
                        <Workflow className="h-5 w-5" />
                      </div>
                      <span className="font-semibold">New Workflow</span>
                    </Link>
                  </Button>
                  <Button className="w-full justify-start h-12 bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 text-white shadow-lg hover:shadow-xl transition-all duration-200" variant="outline" asChild>
                    <Link href="/chat" className="flex items-center gap-4">
                      <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
                        <MessageSquare className="h-5 w-5" />
                      </div>
                      <span className="font-semibold">Start Chat</span>
                    </Link>
                  </Button>
                  <Button className="w-full justify-start h-12 bg-gradient-to-r from-yellow-600 to-yellow-700 hover:from-yellow-700 hover:to-yellow-800 text-white shadow-lg hover:shadow-xl transition-all duration-200" variant="outline" asChild>
                    <Link href="/tools" className="flex items-center gap-4">
                      <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
                        <Zap className="h-5 w-5" />
                      </div>
                      <span className="font-semibold">Manage Tools</span>
                    </Link>
                  </Button>
                </div>
              </StandardCard>

              {/* Enhanced System Status */}
              <StandardCard variant="elevated" title="System Status" description="Service health monitoring">
                {loading ? (
                  <div className="flex items-center justify-center p-4">
                    <RefreshCw className="h-4 w-4 animate-spin text-gray-400" />
                    <span className="ml-2 text-gray-500">Loading services...</span>
                  </div>
                ) : dashboardData?.systemHealth?.services ? (
                  <div className="space-y-3">
                    {Object.entries(dashboardData.systemHealth.services).map(([serviceName, service]) => (
                      <div key={serviceName} className="flex items-center justify-between p-3 rounded-lg border border-gray-200 dark:border-gray-700">
                        <div className="flex items-center gap-3">
                          <div className={cn(
                            "w-2 h-2 rounded-full",
                            (service as ServiceHealth)?.status === 'healthy' ? "bg-green-500" : "bg-red-500"
                          )} />
                          <span className="text-body-sm font-medium capitalize">
                            {serviceName.replace('-', ' ')}
                          </span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-caption text-gray-500">
                            {(service as ServiceHealth)?.response_time_ms?.toFixed(0) || 0}ms
                          </span>
                          <Badge 
                            variant="outline" 
                            className={cn(
                              "text-caption",
                              (service as ServiceHealth)?.status === 'healthy'
                                ? "bg-green-50 text-green-700 border-green-200 dark:bg-green-900/20 dark:text-green-300 dark:border-green-800"
                                : "bg-red-50 text-red-700 border-red-200 dark:bg-red-900/20 dark:text-red-300 dark:border-red-800"
                            )}
                          >
                            {(service as ServiceHealth)?.status === 'healthy' ? 'Online' : 'Offline'}
                          </Badge>
                        </div>
                      </div>
                    ))}
                    {/* Gateway Service */}
                    <div className="flex items-center justify-between p-3 rounded-lg border border-gray-200 dark:border-gray-700">
                      <div className="flex items-center gap-3">
                        <div className="w-2 h-2 rounded-full bg-green-500" />
                        <span className="text-body-sm font-medium">Gateway Service</span>
                      </div>
                      <Badge variant="outline" className="text-caption bg-green-50 text-green-700 border-green-200 dark:bg-green-900/20 dark:text-green-300 dark:border-green-800">
                        Online
                      </Badge>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-3">
                    <div className="flex items-center justify-between p-3 rounded-lg border border-gray-200 dark:border-gray-700">
                      <div className="flex items-center gap-3">
                        <div className="w-2 h-2 rounded-full bg-green-500" />
                        <span className="text-body-sm font-medium">Gateway Service</span>
                      </div>
                      <Badge variant="outline" className="text-caption bg-green-50 text-green-700 border-green-200 dark:bg-green-900/20 dark:text-green-300 dark:border-green-800">
                        Online
                      </Badge>
                    </div>
                    <div className="flex items-center justify-between p-3 rounded-lg border border-gray-200 dark:border-gray-700">
                      <div className="flex items-center gap-3">
                        <div className="w-2 h-2 rounded-full bg-gray-400" />
                        <span className="text-body-sm font-medium">Other Services</span>
                      </div>
                      <Badge variant="outline" className="text-caption bg-gray-50 text-gray-700 border-gray-200 dark:bg-gray-800 dark:text-gray-300 dark:border-gray-700">
                        Unknown
                      </Badge>
                    </div>
                  </div>
                )}
              </StandardCard>
            </div>
          </StandardGrid>
        </StandardSection>
      </StandardPageLayout>
    </AuthGuard>
  );
}
