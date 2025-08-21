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
        description="Monitor your multi-agent system performance and activity"
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

        {/* Error Banner */}
        {error && (
          <StandardSection>
            <StandardCard variant="outlined" className="border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-900/10">
              <div className="flex flex-col sm:flex-row sm:items-center gap-3">
                <div className="flex items-start gap-2 flex-1 min-w-0">
                  <AlertCircle className="h-5 w-5 text-red-500 flex-shrink-0 mt-0.5" />
                  <span className="text-body-sm text-red-700 dark:text-red-300 break-words">
                    Failed to fetch dashboard data: {error}
                  </span>
                </div>
                <Button variant="outline" size="sm" onClick={refresh} className="flex-shrink-0">
                  Retry
                </Button>
              </div>
            </StandardCard>
          </StandardSection>
        )}

        {/* System Health Banner */}
        <StandardSection>
          <StandardCard>
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

        {/* Metrics Cards */}
        <StandardSection>
          <StandardGrid cols={{ default: 1, sm: 2, lg: 4 }} gap="md">
            <StandardCard variant="default" className="transition-all duration-200 hover:shadow-md">
              <div className="flex flex-row items-center justify-between space-y-0 pb-2">
                <h3 className="text-body-sm font-medium text-gray-700 dark:text-gray-300">Active Agents</h3>
                <Bot className="h-4 w-4 text-blue-600 flex-shrink-0" />
              </div>
              <div className="pt-0">
                <div className="text-3xl font-bold text-gray-900 dark:text-white">{metrics.activeAgents}</div>
                <p className="text-caption text-gray-600 dark:text-gray-400 flex items-center gap-1 mt-1">
                  <TrendingUp className="h-3 w-3 flex-shrink-0" />
                  <span className="truncate">
                    {metrics.healthyServices > 0 ? 'Services online' : 'Waiting for services'}
                  </span>
                </p>
              </div>
            </StandardCard>

            <StandardCard variant="default" className="transition-all duration-200 hover:shadow-md">
              <div className="flex flex-row items-center justify-between space-y-0 pb-2">
                <h3 className="text-body-sm font-medium text-gray-700 dark:text-gray-300">Running Workflows</h3>
                <Workflow className="h-4 w-4 text-green-600 flex-shrink-0" />
              </div>
              <div className="pt-0">
                <div className="text-3xl font-bold text-gray-900 dark:text-white">{metrics.runningWorkflows}</div>
                <p className="text-caption text-gray-600 dark:text-gray-400 flex items-center gap-1 mt-1">
                  <Activity className="h-3 w-3 flex-shrink-0" />
                  <span className="truncate">
                    {metrics.runningWorkflows > 0 ? `${metrics.runningWorkflows} queued` : 'No active workflows'}
                  </span>
                </p>
              </div>
            </StandardCard>

            <StandardCard variant="default" className="transition-all duration-200 hover:shadow-md">
              <div className="flex flex-row items-center justify-between space-y-0 pb-2">
                <h3 className="text-body-sm font-medium text-gray-700 dark:text-gray-300">A2A Messages</h3>
                <MessageSquare className="h-4 w-4 text-purple-600 flex-shrink-0" />
              </div>
              <div className="pt-0">
                <div className="text-3xl font-bold text-gray-900 dark:text-white">{metrics.a2aMessages}</div>
                <p className="text-caption text-gray-600 dark:text-gray-400 flex items-center gap-1 mt-1">
                  <TrendingUp className="h-3 w-3 flex-shrink-0" />
                  <span className="truncate">
                    {dashboardData ? 'Live updating' : 'Static count'}
                  </span>
                </p>
              </div>
            </StandardCard>

            <StandardCard variant="default" className="transition-all duration-200 hover:shadow-md">
              <div className="flex flex-row items-center justify-between space-y-0 pb-2">
                <h3 className="text-body-sm font-medium text-gray-700 dark:text-gray-300">Avg Response Time</h3>
                <Zap className="h-4 w-4 text-yellow-600 flex-shrink-0" />
              </div>
              <div className="pt-0">
                <div className="text-3xl font-bold text-gray-900 dark:text-white">
                  {metrics.responseTime > 0 ? `${Math.round(metrics.responseTime)}ms` : 'N/A'}
                </div>
                <p className="text-caption text-gray-600 dark:text-gray-400 flex items-center gap-1 mt-1">
                  <TrendingUp className="h-3 w-3 flex-shrink-0" />
                  <span className="truncate">
                    {metrics.healthyServices}/{metrics.totalServices} services
                  </span>
                </p>
              </div>
            </StandardCard>
          </StandardGrid>
        </StandardSection>

        <StandardSection>
          <StandardGrid cols={{ default: 1, lg: 3 }} gap="lg">
            {/* Recent Activity */}
            <div className="lg:col-span-2">
              <StandardCard title="Recent Activity" 
                actions={
                  <Button variant="outline" size="sm" asChild className="flex-shrink-0">
                    <Link href="/observability">View All</Link>
                  </Button>
                }>
                {loading ? (
                  <div className="flex items-center justify-center p-8">
                    <RefreshCw className="h-6 w-6 animate-spin text-gray-400" />
                    <span className="ml-2 text-gray-500">Loading activity...</span>
                  </div>
                ) : recentActivity.length > 0 ? (
                  <div className="space-y-4">
                    {recentActivity.map((activity) => (
                      <div key={activity.id} className="flex items-start gap-3 p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                        <div className="flex-shrink-0 mt-1">
                          <div className="flex items-center justify-center w-8 h-8 rounded-full bg-gray-100 dark:bg-gray-800">
                            {getActivityTypeIcon(activity.type)}
                          </div>
                        </div>
                        <div className="flex-grow min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <p className="font-medium text-body-sm text-gray-900 dark:text-white truncate">
                              {activity.title}
                            </p>
                            <div className="flex-shrink-0">
                              {getStatusIcon(activity.status)}
                            </div>
                          </div>
                          <p className="text-body-sm text-gray-600 dark:text-gray-300 line-clamp-2">
                            {activity.description}
                          </p>
                          <p className="text-caption text-gray-500 dark:text-gray-400 mt-1">
                            {formatTimestamp(activity.timestamp)}
                          </p>
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

            {/* Sidebar */}
            <div className="space-y-6">
              {/* Quick Actions */}
              <StandardCard title="Quick Actions">
                <div className="space-y-3">
                  <Button className="w-full justify-start h-11" asChild>
                    <Link href="/agents" className="flex items-center gap-3">
                      <Bot className="h-4 w-4" />
                      <span>Create Agent</span>
                    </Link>
                  </Button>
                  <Button className="w-full justify-start h-11" variant="outline" asChild>
                    <Link href="/workflows" className="flex items-center gap-3">
                      <Workflow className="h-4 w-4" />
                      <span>New Workflow</span>
                    </Link>
                  </Button>
                  <Button className="w-full justify-start h-11" variant="outline" asChild>
                    <Link href="/chat" className="flex items-center gap-3">
                      <MessageSquare className="h-4 w-4" />
                      <span>Start Chat</span>
                    </Link>
                  </Button>
                  <Button className="w-full justify-start h-11" variant="outline" asChild>
                    <Link href="/tools" className="flex items-center gap-3">
                      <Zap className="h-4 w-4" />
                      <span>Manage Tools</span>
                    </Link>
                  </Button>
                </div>
              </StandardCard>

              {/* System Status */}
              <StandardCard title="System Status">
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
