import { useState, useEffect, useCallback } from 'react';
import { simpleDashboardApi, DashboardData } from '@/lib/simpleDashboardApi';

interface UseDashboardDataOptions {
  refreshInterval?: number; // in milliseconds
  autoRefresh?: boolean;
}

interface UseDashboardDataReturn {
  data: DashboardData | null;
  loading: boolean;
  error: string | null;
  lastUpdated: Date | null;
  refresh: () => Promise<void>;
}

export function useDashboardData(
  options: UseDashboardDataOptions = {}
): UseDashboardDataReturn {
  const { refreshInterval = 30000, autoRefresh = true } = options; // 30 seconds default
  
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setError(null);
      const stats = await simpleDashboardApi.getDashboardData();
      setData(stats);
      setLastUpdated(new Date());
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch dashboard data';
      setError(errorMessage);
      console.error('Dashboard data fetch error:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const refresh = useCallback(async () => {
    setLoading(true);
    await fetchData();
  }, [fetchData]);

  // Initial data fetch
  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Auto refresh setup
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(fetchData, refreshInterval);
    return () => clearInterval(interval);
  }, [fetchData, refreshInterval, autoRefresh]);

  return {
    data,
    loading,
    error,
    lastUpdated,
    refresh
  };
}

// Hook for real-time system health status
export function useSystemHealth() {
  const [systemHealth, setSystemHealth] = useState<{
    status: string;
    uptime: string;
    servicesCount: { total: number; healthy: number };
  } | null>(null);

  const { data } = useDashboardData({ refreshInterval: 10000 }); // 10 seconds for health

  useEffect(() => {
    if (data?.metrics) {
      setSystemHealth({
        status: data.metrics.systemHealth,
        uptime: '2d 5h 30m', // Using static uptime for now
        servicesCount: {
          total: data.metrics.totalServices,
          healthy: data.metrics.healthyServices
        }
      });
    }
  }, [data]);

  return systemHealth;
}

// Hook for metrics with automatic incremental updates
export function useLiveMetrics() {
  const { data } = useDashboardData();
  const [liveMetrics, setLiveMetrics] = useState(data?.metrics || null);

  useEffect(() => {
    if (data?.metrics) {
      setLiveMetrics(data.metrics);
    }
  }, [data]);

  // Simulate live updates for certain metrics when services are healthy
  useEffect(() => {
    if (!liveMetrics || !data?.metrics) return;

    const healthyServicesCount = data.metrics.healthyServices;

    if (healthyServicesCount === 0) return;

    const interval = setInterval(() => {
      setLiveMetrics(prev => {
        if (!prev) return prev;
        
        return {
          ...prev,
          // Simulate realistic incremental changes
          a2aMessages: prev.a2aMessages + Math.floor(Math.random() * 3) + 1,
          responseTime: Math.max(50, Math.min(500, prev.responseTime + (Math.random() - 0.5) * 20)),
        };
      });
    }, 5000); // Update every 5 seconds

    return () => clearInterval(interval);
  }, [liveMetrics, data?.metrics]);

  return liveMetrics;
}
