'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useProject } from '@/store/projectContext';
import { useAuth, useUser } from '@/store/authContext';
import { useSidebarStats } from '@/hooks/useSidebarStats';
import { 
  LayoutDashboard,
  MessageSquare,
  Bot,
  Workflow,
  Zap,
  Database,
  Activity,
  Settings,
  Menu,
  X,
  ChevronDown,
  ChevronRight,
  FolderOpen,
  Check,
  LogOut,
  User
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface NavigationItem {
  id: string;
  label: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: string;
  children?: NavigationItem[];
}

const navigationItems: NavigationItem[] = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    href: '/dashboard',
    icon: LayoutDashboard
  },
  {
    id: 'projects',
    label: 'Projects',
    href: '/projects',
    icon: FolderOpen
  },
  {
    id: 'chat',
    label: 'Chat Interface',
    href: '/chat',
    icon: MessageSquare
  },
  {
    id: 'agents',
    label: 'Agents',
    href: '/agents',
    icon: Bot
  },
  {
    id: 'workflows',
    label: 'Workflows',
    href: '/workflows',
    icon: Workflow
  },
  {
    id: 'tools',
    label: 'Tools',
    href: '/tools',
    icon: Zap
  },
  {
    id: 'rag',
    label: 'RAG Management',
    href: '/rag',
    icon: Database
  },
  {
    id: 'environment',
    label: 'Environment',
    href: '/environment',
    icon: Settings
  },
  {
    id: 'observability',
    label: 'Observability',
    href: '/observability',
    icon: Activity
  },
  {
    id: 'settings',
    label: 'Settings',
    href: '/settings',
    icon: Settings
  }
];

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

function Sidebar({ isOpen, onClose }: SidebarProps) {
  const pathname = usePathname();
  const [expandedItems, setExpandedItems] = useState<string[]>([]);
  const [showProjectDropdown, setShowProjectDropdown] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const { state, selectProject } = useProject();
  const { state: authState, logout } = useAuth();
  const user = useUser();
  const { stats } = useSidebarStats();

  // Create navigation items with real badge counts
  const navigationItemsWithBadges = navigationItems.map(item => {
    let badge: string | undefined;
    
    switch (item.id) {
      case 'agents':
        badge = stats.agents > 0 ? stats.agents.toString() : undefined;
        break;
      case 'workflows':
        badge = stats.workflows > 0 ? stats.workflows.toString() : undefined;
        break;
      case 'tools':
        badge = stats.tools > 0 ? stats.tools.toString() : undefined;
        break;
      case 'projects':
        badge = stats.projects > 0 ? stats.projects.toString() : undefined;
        break;
      default:
        badge = undefined;
    }
    
    return { ...item, badge };
  });

  const toggleExpanded = (itemId: string) => {
    setExpandedItems(prev => 
      prev.includes(itemId) 
        ? prev.filter(id => id !== itemId)
        : [...prev, itemId]
    );
  };

  const isActive = (href: string) => {
    if (href === '/' && pathname === '/') return true;
    if (href !== '/' && pathname.startsWith(href)) return true;
    return false;
  };

  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  const getUserInitials = (user: any) => {
    if (user?.firstName && user?.lastName) {
      return `${user.firstName[0]}${user.lastName[0]}`.toUpperCase();
    }
    if (user?.username) {
      return user.username.slice(0, 2).toUpperCase();
    }
    if (user?.email) {
      return user.email.slice(0, 2).toUpperCase();
    }
    return 'U';
  };

  const getUserDisplayName = (user: any) => {
    if (user?.firstName && user?.lastName) {
      return `${user.firstName} ${user.lastName}`;
    }
    if (user?.username) {
      return user.username;
    }
    if (user?.email) {
      return user.email.split('@')[0];
    }
    return 'User';
  };

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'admin':
        return 'bg-red-100 text-red-800';
      case 'user':
        return 'bg-blue-100 text-blue-800';
      case 'viewer':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <>
      {/* Overlay for mobile */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <div
        className={cn(
          'fixed top-0 left-0 z-50 h-full w-64 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700 transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0',
          isOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <Bot className="h-5 w-5 text-white" />
            </div>
            <div>
              <h2 className="font-bold text-lg text-gray-900 dark:text-white">
                Agentic AI Accelerator
              </h2>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Multi-Agent System
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="lg:hidden p-1 rounded-md hover:bg-gray-100 dark:hover:bg-gray-800"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Project Selector */}
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="relative">
            <button
              onClick={() => setShowProjectDropdown(!showProjectDropdown)}
              className="w-full flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            >
              <div className="flex items-center space-x-3">
                {state.selectedProject ? (
                  <>
                    <div 
                      className="w-3 h-3 rounded-full"
                      style={{ backgroundColor: state.selectedProject.color }}
                    />
                    <div className="text-left">
                      <p className="text-sm font-medium text-gray-900 dark:text-white">
                        {state.selectedProject.name}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        {state.selectedProject.tags.slice(0, 2).join(', ')}
                        {state.selectedProject.tags.length > 2 && '...'}
                      </p>
                    </div>
                  </>
                ) : (
                  <>
                    <FolderOpen className="w-4 h-4 text-gray-400" />
                    <div className="text-left">
                      <p className="text-sm font-medium text-gray-900 dark:text-white">
                        Select Project
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        No project selected
                      </p>
                    </div>
                  </>
                )}
              </div>
              <ChevronDown className={cn(
                "h-4 w-4 text-gray-400 transition-transform",
                showProjectDropdown && "transform rotate-180"
              )} />
            </button>

            {/* Project Dropdown */}
            {showProjectDropdown && (
              <div className="absolute top-full left-0 right-0 mt-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg z-10 max-h-64 overflow-y-auto">
                <div className="p-2">
                  <div 
                    onClick={() => {
                      selectProject(null);
                      setShowProjectDropdown(false);
                    }}
                    className="flex items-center justify-between p-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer"
                  >
                    <div className="flex items-center space-x-3">
                      <FolderOpen className="w-4 h-4 text-gray-400" />
                      <span className="text-sm text-gray-700 dark:text-gray-300">
                        All Projects
                      </span>
                    </div>
                    {!state.selectedProject && (
                      <Check className="h-4 w-4 text-blue-600 dark:text-blue-400" />
                    )}
                  </div>
                  
                  {state.projects.map((project) => (
                    <div
                      key={project.id}
                      onClick={() => {
                        selectProject(project);
                        setShowProjectDropdown(false);
                      }}
                      className="flex items-center justify-between p-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer"
                    >
                      <div className="flex items-center space-x-3">
                        <div 
                          className="w-3 h-3 rounded-full"
                          style={{ backgroundColor: project.color }}
                        />
                        <div>
                          <p className="text-sm font-medium text-gray-900 dark:text-white">
                            {project.name}
                          </p>
                          <p className="text-xs text-gray-500 dark:text-gray-400">
                            {project.tags.slice(0, 2).join(', ')}
                            {project.tags.length > 2 && '...'}
                          </p>
                        </div>
                      </div>
                      {state.selectedProject?.id === project.id && (
                        <Check className="h-4 w-4 text-blue-600 dark:text-blue-400" />
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4">
          <ul className="space-y-2">
            {navigationItemsWithBadges.map((item) => (
              <li key={item.id}>
                {item.children ? (
                  // Expandable item
                  <div>
                    <button
                      onClick={() => toggleExpanded(item.id)}
                      className={cn(
                        'w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                        'hover:bg-gray-100 dark:hover:bg-gray-800',
                        'text-gray-700 dark:text-gray-300'
                      )}
                    >
                      <div className="flex items-center space-x-3">
                        <item.icon className="h-5 w-5" />
                        <span>{item.label}</span>
                        {item.badge && (
                          <span className="px-2 py-0.5 text-xs bg-blue-100 text-blue-800 rounded-full">
                            {item.badge}
                          </span>
                        )}
                      </div>
                      {expandedItems.includes(item.id) ? (
                        <ChevronDown className="h-4 w-4" />
                      ) : (
                        <ChevronRight className="h-4 w-4" />
                      )}
                    </button>
                    {expandedItems.includes(item.id) && (
                      <ul className="mt-2 ml-8 space-y-1">
                        {item.children.map((child) => (
                          <li key={child.id}>
                            <Link
                              href={child.href}
                              onClick={onClose}
                              className={cn(
                                'flex items-center space-x-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                                isActive(child.href)
                                  ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300'
                                  : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
                              )}
                            >
                              <child.icon className="h-4 w-4" />
                              <span>{child.label}</span>
                              {child.badge && (
                                <span className="px-2 py-0.5 text-xs bg-blue-100 text-blue-800 rounded-full">
                                  {child.badge}
                                </span>
                              )}
                            </Link>
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                ) : (
                  // Regular item
                  <Link
                    href={item.href}
                    onClick={onClose}
                    className={cn(
                      'flex items-center justify-between px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                      isActive(item.href)
                        ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300'
                        : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
                    )}
                  >
                    <div className="flex items-center space-x-3">
                      <item.icon className="h-5 w-5" />
                      <span>{item.label}</span>
                    </div>
                    {item.badge && (
                      <span className="px-2 py-0.5 text-xs bg-blue-100 text-blue-800 rounded-full">
                        {item.badge}
                      </span>
                    )}
                  </Link>
                )}
              </li>
            ))}
          </ul>
        </nav>

        {/* User Section */}
        <div className="p-4 border-t border-gray-200 dark:border-gray-700">
          <div className="relative">
            <button
              onClick={() => setShowUserMenu(!showUserMenu)}
              className="w-full flex items-center space-x-3 p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            >
              <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                <span className="text-sm font-medium text-white">
                  {getUserInitials(user)}
                </span>
              </div>
              <div className="flex-1 text-left min-w-0">
                <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                  {getUserDisplayName(user)}
                </p>
                <div className="flex items-center space-x-2">
                  <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                    {user?.email || 'No email'}
                  </p>
                  {user?.role && (
                    <span className={cn(
                      "text-xs px-1.5 py-0.5 rounded",
                      getRoleColor(user.role)
                    )}>
                      {user.role}
                    </span>
                  )}
                </div>
              </div>
              <ChevronDown className={cn(
                "h-4 w-4 text-gray-400 transition-transform",
                showUserMenu && "transform rotate-180"
              )} />
            </button>

            {/* User Menu */}
            {showUserMenu && (
              <div className="absolute bottom-full left-0 right-0 mb-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg z-10">
                <div className="p-2">
                  <Link
                    href="/settings/profile"
                    onClick={() => setShowUserMenu(false)}
                    className="flex items-center space-x-3 p-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700 text-sm text-gray-700 dark:text-gray-300"
                  >
                    <User className="h-4 w-4" />
                    <span>Profile Settings</span>
                  </Link>
                  <button
                    onClick={() => {
                      setShowUserMenu(false);
                      handleLogout();
                    }}
                    className="w-full flex items-center space-x-3 p-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700 text-sm text-red-600 dark:text-red-400"
                  >
                    <LogOut className="h-4 w-4" />
                    <span>Sign Out</span>
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
}

interface TopBarProps {
  onMenuClick: () => void;
}

function TopBar({ onMenuClick }: TopBarProps) {
  const { stats } = useSidebarStats();
  const user = useUser();
  
  const getStatusColor = (health: string) => {
    switch (health) {
      case 'healthy': return 'bg-green-500';
      case 'degraded': return 'bg-yellow-500';
      case 'unhealthy': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };
  
  const getStatusText = (health: string) => {
    switch (health) {
      case 'healthy': return 'All Systems Operational';
      case 'degraded': return 'Some Services Degraded';
      case 'unhealthy': return 'System Issues Detected';
      default: return 'System Status Unknown';
    }
  };

  const getUserInitials = (user: any) => {
    if (user?.firstName && user?.lastName) {
      return `${user.firstName[0]}${user.lastName[0]}`.toUpperCase();
    }
    if (user?.username) {
      return user.username.slice(0, 2).toUpperCase();
    }
    if (user?.email) {
      return user.email.slice(0, 2).toUpperCase();
    }
    return 'U';
  };

  return (
    <header className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 px-4 py-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={onMenuClick}
            className="lg:hidden p-1 rounded-md hover:bg-gray-100 dark:hover:bg-gray-800"
          >
            <Menu className="h-6 w-6" />
          </button>
          <div className="hidden lg:block">
            <h1 className="text-xl font-semibold text-gray-900 dark:text-white">
              Multi-Agent Platform
            </h1>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          {/* Status indicator */}
          <div className="flex items-center space-x-2">
            <div className={cn("w-2 h-2 rounded-full", getStatusColor(stats.systemHealth))}></div>
            <span className="text-sm text-gray-600 dark:text-gray-400">
              {getStatusText(stats.systemHealth)}
            </span>
          </div>

          {/* User menu */}
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
              <span className="text-sm font-medium text-white">
                {getUserInitials(user)}
              </span>
            </div>
            {user && (
              <div className="hidden md:block">
                <p className="text-sm font-medium text-gray-900 dark:text-white">
                  {user.firstName && user.lastName 
                    ? `${user.firstName} ${user.lastName}`
                    : user.username || user.email?.split('@')[0] || 'User'
                  }
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}

export default function Navigation({ children }: { children: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { state: authState } = useAuth();

  // Don't show navigation if user is not authenticated
  if (!authState.isAuthenticated) {
    return <>{children}</>;
  }

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      
      <div className="flex-1 flex flex-col overflow-hidden lg:ml-0">
        <TopBar onMenuClick={() => setSidebarOpen(true)} />
        
        <main className="flex-1 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  );
}
