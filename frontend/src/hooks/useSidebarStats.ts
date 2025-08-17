import { useState, useEffect } from 'react';

interface SidebarStats {
  agents: number;
  projects: number;
  workflows: number;
  tools: number;
  lastUpdated: string;
  systemHealth: string;
  error?: string;
}

export function useSidebarStats() {
  const [stats, setStats] = useState<SidebarStats>({
    agents: 0,
    projects: 1,
    workflows: 0,
    tools: 0,
    lastUpdated: '',
    systemHealth: 'unknown',
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = async () => {
    try {
      const response = await fetch('/api/sidebar');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      
      // Transform the response to match our interface
      const transformedStats: SidebarStats = {
        agents: parseInt(data.badges?.agents || '0', 10),
        workflows: parseInt(data.badges?.workflows || '0', 10),
        tools: parseInt(data.badges?.tools || '0', 10),
        projects: 1, // Keep as fixed for now
        lastUpdated: data.lastUpdated || new Date().toISOString(),
        systemHealth: data.systemHealth || 'unknown',
        error: data.error,
      };
      
      setStats(transformedStats);
      setError(data.error || null);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch sidebar stats';
      setError(errorMessage);
      console.error('Sidebar stats fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
    
    // Refresh stats every 30 seconds
    const interval = setInterval(fetchStats, 30000);
    
    return () => clearInterval(interval);
  }, []);

  return { stats, loading, error, refresh: fetchStats };
}
