'use client';

import { useState, useEffect } from 'react';
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
  User,
  Search,
  Bell,
  Plus,
  Home,
  Maximize2,
  Minimize2,
  Command,
  Star,
  Filter,
  MoreHorizontal,
  Bookmark,
  Clock,
  TrendingUp,
  AlertCircle,
  HelpCircle,
  Brain,
  TestTube,
  PanelLeftClose,
  PanelLeftOpen,
  Sparkles
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { NotificationBell } from '@/components/ui/notification-bell';

interface NavigationItem {
  id: string;
  label: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: string;
  children?: NavigationItem[];
  shortcut?: string;
}

interface NavigationSection {
  id: string;
  label: string;
  items: NavigationItem[];
}

const navigationSections = [
  {
    id: 'overview',
    label: 'Overview',
    items: [
      {
        id: 'dashboard',
        label: 'Dashboard',
        href: '/dashboard',
        icon: LayoutDashboard,
        description: 'System overview and analytics',
        shortcut: '⌘D'
      },
      {
        id: 'projects',
        label: 'Projects',
        href: '/projects',
        icon: FolderOpen,
        description: 'Manage your projects',
        shortcut: '⌘P'
      }
    ]
  },
  {
    id: 'workspace',
    label: 'Workspace',
    items: [
      {
        id: 'chat',
        label: 'AI Chat',
        href: '/chat',
        icon: MessageSquare,
        description: 'Interactive AI conversations',
        shortcut: '⌘C',
        highlight: true
      },
      {
        id: 'agents',
        label: 'Agents',
        href: '/agents',
        icon: Bot,
        description: 'AI agent management',
        children: [
          {
            id: 'agents-active',
            label: 'Active Agents',
            href: '/agents?status=active',
            icon: TrendingUp,
            description: 'Currently running agents'
          },
          {
            id: 'agents-templates',
            label: 'Templates',
            href: '/agents/templates',
            icon: Star,
            description: 'Pre-built agent templates'
          }
        ]
      },
      {
        id: 'workflows',
        label: 'Workflows',
        href: '/workflows',
        icon: Workflow,
        description: 'Automated processes'
      },
      {
        id: 'tools',
        label: 'Tools',
        href: '/tools',
        icon: Zap,
        description: 'Available tools and integrations',
        children: [
          {
            id: 'tools-templates',
            label: 'Templates',
            href: '/templates/tools',
            icon: Star,
            description: 'Tool templates'
          }
        ]
      }
    ]
  },
  {
    id: 'platform',
    label: 'Platform',
    items: [
      {
        id: 'mcp',
        label: 'MCP Hub',
        href: '/mcp',
        icon: Command,
        description: 'Model Context Protocol management',
        children: [
          {
            id: 'mcp-servers',
            label: 'Servers',
            href: '/mcp?tab=servers',
            icon: Bot,
            description: 'MCP server instances'
          },
          {
            id: 'mcp-endpoints',
            label: 'Endpoints',
            href: '/mcp?tab=endpoints',
            icon: Zap,
            description: 'Gateway endpoints'
          },
          {
            id: 'mcp-tools',
            label: 'Tools',
            href: '/mcp?tab=tools',
            icon: Command,
            description: 'Discovered MCP tools'
          },
          {
            id: 'mcp-tester',
            label: 'Tool Tester',
            href: '/mcp?tab=tester',
            icon: TestTube
          }
        ]
      }
    ]
  },
  {
    id: 'models',
    label: 'Model Management',
    items: [
      {
        id: 'llm-models',
        label: 'LLM Models',
        href: '/models/llm-models',
        icon: Bot,
        children: [
          {
            id: 'llm-models-active',
            label: 'Active Models',
            href: '/models/llm-models?status=active',
            icon: TrendingUp
          },
          {
            id: 'llm-models-all',
            label: 'All Models',
            href: '/models/llm-models',
            icon: Bot
          }
        ]
      },
      {
        id: 'embedding-models',
        label: 'Embedding Models',
        href: '/models/embedding-models',
        icon: Brain,
        children: [
          {
            id: 'embedding-models-active',
            label: 'Active Models',
            href: '/models/embedding-models?status=active',
            icon: TrendingUp
          },
          {
            id: 'embedding-models-all',
            label: 'All Models',
            href: '/models/embedding-models',
            icon: Brain
          }
        ]
      }
    ]
  },
  {
    id: 'data',
    label: 'Data & Storage',
    items: [
      {
        id: 'rag',
        label: 'RAG Management',
        href: '/rag',
        icon: Database
      }
    ]
  },
  {
    id: 'system',
    label: 'System',
    items: [
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
      }
    ]
  }
];

const quickActions = [
  {
    id: 'new-agent',
    label: 'New Agent',
    href: '/agents?action=create',
    icon: Bot,
    color: 'bg-blue-500'
  },
  {
    id: 'new-workflow',
    label: 'New Workflow',
    href: '/workflows?action=create',
    icon: Workflow,
    color: 'bg-green-500'
  },
  {
    id: 'new-tool',
    label: 'New Tool',
    href: '/tools?action=create',
    icon: Zap,
    color: 'bg-purple-500'
  }
];

const recentItems = [
  {
    id: 'recent-chat',
    label: 'Customer Support Chat',
    href: '/chat/session-123',
    icon: MessageSquare,
    timestamp: '2 min ago'
  },
  {
    id: 'recent-agent',
    label: 'Data Analysis Agent',
    href: '/agents/agent-456',
    icon: Bot,
    timestamp: '5 min ago'
  },
  {
    id: 'recent-workflow',
    label: 'Invoice Processing',
    href: '/workflows/workflow-789',
    icon: Workflow,
    timestamp: '10 min ago'
  }
];

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
}

function Sidebar({ isOpen, onClose, isCollapsed, onToggleCollapse }: SidebarProps) {
  const pathname = usePathname();
  const [expandedItems, setExpandedItems] = useState<string[]>([]);
  const [expandedSections, setExpandedSections] = useState<string[]>(['main', 'workspace']);
  const [showProjectDropdown, setShowProjectDropdown] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTab, setActiveTab] = useState<'nav' | 'recent'>('nav');
  const { state, selectProject } = useProject();
  const { state: authState, logout } = useAuth();
  const user = useUser();
  const { stats } = useSidebarStats();

  // Auto-collapse sections when sidebar is collapsed
  useEffect(() => {
    if (isCollapsed) {
      setExpandedSections([]);
      setExpandedItems([]);
      setShowProjectDropdown(false);
      setShowUserMenu(false);
    } else {
      setExpandedSections(['main', 'workspace']);
    }
  }, [isCollapsed]);

  // Add badge counts to navigation items
  const getNavigationWithBadges = () => {
    if (!stats) return navigationSections;
    
    return navigationSections.map(section => ({
      ...section,
      items: section.items.map(item => {
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
      })
    }));
  };

  const toggleExpanded = (itemId: string) => {
    if (isCollapsed) return;
    setExpandedItems(prev => 
      prev.includes(itemId) 
        ? prev.filter(id => id !== itemId)
        : [...prev, itemId]
    );
  };

  const toggleSection = (sectionId: string) => {
    if (isCollapsed) return;
    setExpandedSections(prev => 
      prev.includes(sectionId) 
        ? prev.filter(id => id !== sectionId)
        : [...prev, sectionId]
    );
  };

  const navSections = getNavigationWithBadges();
  const filteredNavigation = (Array.isArray(navSections) ? navSections : []).map(section => ({
    ...section,
    items: section.items.filter(item => 
      item.label.toLowerCase().includes(searchQuery.toLowerCase())
    )
  })).filter(section => section.items.length > 0);

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
          'fixed top-0 left-0 z-50 h-full bg-white/95 backdrop-blur-xl dark:bg-gray-900/95 border-r border-gray-200/50 dark:border-gray-700/50 transform transition-all duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0 flex flex-col shadow-2xl lg:shadow-none',
          isCollapsed ? 'w-20' : 'w-72',
          isOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        {/* Header */}
        <div className={cn(
          'flex items-center border-b border-gray-200/50 dark:border-gray-700/50 p-4 min-h-[4.5rem] bg-gradient-to-r from-blue-50 to-purple-50 dark:from-gray-800 dark:to-gray-800',
          isCollapsed ? 'justify-center px-2' : 'justify-between'
        )}>
          {!isCollapsed && (
            <div className="flex items-center gap-3 min-w-0 flex-1">
              <div className="relative">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-600 via-purple-600 to-blue-700 rounded-xl flex items-center justify-center shadow-2xl flex-shrink-0 ring-2 ring-white/20">
                  <Sparkles className="h-6 w-6 text-white" />
                </div>
                <div className="absolute -top-1 -right-1 w-4 h-4 bg-green-400 rounded-full border-2 border-white dark:border-gray-900 animate-pulse"></div>
              </div>
              <div className="min-w-0 flex-1">
                <h2 className="font-bold text-xl bg-gradient-to-r from-gray-900 to-gray-700 dark:from-white dark:to-gray-300 bg-clip-text text-transparent truncate">
                  Agentic AI
                </h2>
                <p className="text-xs font-medium text-blue-600 dark:text-blue-400 truncate">
                  Enterprise Platform
                </p>
              </div>
            </div>
          )}
          {isCollapsed && (
            <div className="relative">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-600 via-purple-600 to-blue-700 rounded-xl flex items-center justify-center shadow-2xl ring-2 ring-white/20">
                <Sparkles className="h-6 w-6 text-white" />
              </div>
              <div className="absolute -top-1 -right-1 w-4 h-4 bg-green-400 rounded-full border-2 border-white dark:border-gray-900 animate-pulse"></div>
            </div>
          )}
          <div className="flex items-center gap-1 flex-shrink-0">
            <button
              onClick={onToggleCollapse}
              className="hidden lg:flex p-2 rounded-lg hover:bg-white/20 dark:hover:bg-gray-700/50 transition-all duration-200 backdrop-blur-sm group"
              title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
            >
              {isCollapsed ? <PanelLeftOpen className="h-5 w-5 group-hover:scale-110 transition-transform" /> : <PanelLeftClose className="h-5 w-5 group-hover:scale-110 transition-transform" />}
            </button>
            <button
              onClick={onClose}
              className="lg:hidden p-1.5 rounded-md hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* Search & Quick Actions */}
        {!isCollapsed && (
          <div className="p-4 border-b border-gray-200/50 dark:border-gray-700/50 space-y-4 bg-gradient-to-b from-gray-50/50 to-transparent dark:from-gray-800/30">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400 flex-shrink-0" />
              <input
                type="text"
                placeholder="Search agents, workflows..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-12 pr-12 py-3 bg-white/80 dark:bg-gray-800/80 border border-gray-200/50 dark:border-gray-600/50 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 focus:bg-white dark:focus:bg-gray-800 backdrop-blur-sm transition-all duration-200 shadow-sm"
              />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery('')}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                >
                  <X className="h-4 w-4" />
                </button>
              )}
            </div>

            {/* Quick Actions */}
            <div className="grid grid-cols-3 gap-3">
              {quickActions.map((action) => (
                <Link
                  key={action.id}
                  href={action.href}
                  className="flex flex-col items-center p-3 rounded-xl hover:bg-white/60 dark:hover:bg-gray-800/60 transition-all duration-200 group backdrop-blur-sm border border-gray-200/30 dark:border-gray-600/30 hover:shadow-lg hover:scale-105"
                  title={action.label}
                >
                  <div className={cn(
                    "w-10 h-10 rounded-xl flex items-center justify-center mb-2 group-hover:scale-110 transition-all duration-200 shadow-lg ring-2 ring-white/20",
                    action.color
                  )}>
                    <action.icon className="h-5 w-5 text-white" />
                  </div>
                  <span className="text-xs font-medium text-gray-700 dark:text-gray-300 text-center leading-tight">
                    {action.label.split(' ')[1] || action.label}
                  </span>
                </Link>
              ))}
            </div>
          </div>
        )}

        {/* Project Selector */}
        {!isCollapsed && (
          <div className="p-4 border-b border-gray-200/50 dark:border-gray-700/50">
            <div className="relative">
              <button
                onClick={() => setShowProjectDropdown(!showProjectDropdown)}
                className="w-full flex items-center justify-between p-4 bg-gradient-to-r from-white/80 to-gray-50/80 dark:from-gray-800/80 dark:to-gray-700/80 rounded-xl hover:from-white hover:to-gray-50 dark:hover:from-gray-700 dark:hover:to-gray-600 transition-all duration-200 min-h-[4rem] backdrop-blur-sm border border-gray-200/30 dark:border-gray-600/30 shadow-sm hover:shadow-md"
              >
                <div className="flex items-center gap-3 min-w-0 flex-1">
                  {state.selectedProject ? (
                    <>
                      <div className="relative">
                        <div 
                          className="w-4 h-4 rounded-full flex-shrink-0 ring-2 ring-white/50 shadow-sm"
                          style={{ backgroundColor: state.selectedProject.color }}
                        />
                        <div className="absolute -top-1 -right-1 w-2 h-2 bg-green-400 rounded-full border border-white dark:border-gray-800 animate-pulse"></div>
                      </div>
                      <div className="text-left min-w-0 flex-1">
                        <p className="text-sm font-semibold text-gray-900 dark:text-white truncate">
                          {state.selectedProject.name}
                        </p>
                        <p className="text-xs font-medium text-gray-600 dark:text-gray-400 truncate">
                          {state.selectedProject.tags.slice(0, 2).join(' • ')}
                          {state.selectedProject.tags.length > 2 && ' • ...'}
                        </p>
                      </div>
                    </>
                  ) : (
                    <>
                      <div className="w-4 h-4 rounded-full bg-gray-200 dark:bg-gray-600 flex items-center justify-center flex-shrink-0">
                        <FolderOpen className="w-3 h-3 text-gray-500 dark:text-gray-400" />
                      </div>
                      <div className="text-left min-w-0 flex-1">
                        <p className="text-sm font-semibold text-gray-900 dark:text-white">
                          Select Project
                        </p>
                        <p className="text-xs font-medium text-gray-600 dark:text-gray-400">
                          Choose your workspace
                        </p>
                      </div>
                    </>
                  )}
                </div>
                <ChevronDown className={cn(
                  "h-4 w-4 text-gray-400 transition-transform flex-shrink-0",
                  showProjectDropdown && "transform rotate-180"
                )} />
              </button>

              {/* Project Dropdown */}
              {showProjectDropdown && (
                <div className="absolute top-full left-0 right-0 mt-2 bg-white/95 dark:bg-gray-800/95 backdrop-blur-xl border border-gray-200/50 dark:border-gray-600/50 rounded-xl shadow-2xl z-10 max-h-64 overflow-y-auto">
                  <div className="p-2">
                    <div 
                      onClick={() => {
                        selectProject(null);
                        setShowProjectDropdown(false);
                      }}
                      className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-100/80 dark:hover:bg-gray-700/80 cursor-pointer transition-all duration-150"
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
                        className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-100/80 dark:hover:bg-gray-700/80 cursor-pointer transition-all duration-150"
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
        )}

        {/* Navigation Tabs */}
        {!isCollapsed && (
          <div className="flex border-b border-gray-200 dark:border-gray-700">
            {[
              { id: 'nav', label: 'Navigation', icon: Menu }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={cn(
                  'flex-1 flex items-center justify-center space-x-1 px-3 py-2 text-xs font-medium transition-colors border-b-2',
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/20'
                    : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
                )}
              >
                <tab.icon className="h-3 w-3" />
                <span>{tab.label}</span>
              </button>
            ))}
          </div>
        )}

        {/* Navigation Content */}
        <div className="flex-1 overflow-y-auto scrollbar-thin">
          {activeTab === 'nav' && (
            <nav className="p-4">
              {(searchQuery 
                ? [{ id: 'search-results', label: 'Search Results', items: Array.isArray(filteredNavigation) ? filteredNavigation.flatMap(s => s.items) : [] } as NavigationSection] 
                : filteredNavigation
              ).map((section) => (
                <div key={section.id} className="mb-6">
                  {!isCollapsed && !searchQuery && (
                    <button
                      onClick={() => toggleSection(section.id)}
                      className="flex items-center justify-between w-full mb-2 px-2 py-1 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider hover:text-gray-700 dark:hover:text-gray-300 transition-colors"
                    >
                      <span>{section.label}</span>
                      {expandedSections.includes(section.id) ? (
                        <ChevronDown className="h-3 w-3" />
                      ) : (
                        <ChevronRight className="h-3 w-3" />
                      )}
                    </button>
                  )}
                  
                  {(isCollapsed || expandedSections.includes(section.id) || searchQuery) && (
                    <ul className="space-y-1">
                      {section.items.map((item) => (
                        <li key={item.id}>
                          {'children' in item && item.children && !isCollapsed ? (
                            // Expandable item
                            <div>
                              <button
                                onClick={() => toggleExpanded(item.id)}
                                className={cn(
                                  'w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm font-medium transition-all group',
                                  'hover:bg-gray-100 dark:hover:bg-gray-800',
                                  'text-gray-700 dark:text-gray-300'
                                )}
                              >
                                <div className="flex items-center space-x-3">
                                  <item.icon className="h-4 w-4 group-hover:scale-110 transition-transform" />
                                  <span>{item.label}</span>
                                  {item.shortcut && (
                                    <span className="ml-auto text-xs text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity">
                                      {item.shortcut}
                                    </span>
                                  )}
                                  {item.badge && (
                                    <span className="px-2 py-0.5 text-xs bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300 rounded-full">
                                      {item.badge}
                                    </span>
                                  )}
                                </div>
                                <ChevronRight className={cn(
                                  "h-3 w-3 transition-transform",
                                  expandedItems.includes(item.id) && "rotate-90"
                                )} />
                              </button>
                              {expandedItems.includes(item.id) && (
                                <ul className="mt-1 ml-8 space-y-1">
                                  {item.children.map((child) => (
                                    <li key={child.id}>
                                      <Link
                                        href={child.href}
                                        onClick={onClose}
                                        className={cn(
                                          'flex items-center space-x-3 px-3 py-2 rounded-lg text-sm font-medium transition-all group',
                                          isActive(child.href)
                                            ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg transform scale-105'
                                            : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-gray-100'
                                        )}
                                      >
                                        <child.icon className="h-4 w-4 group-hover:scale-110 transition-transform" />
                                        <span>{child.label}</span>
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
                                'flex items-center justify-between px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 group relative overflow-hidden',
                                isActive(item.href)
                                  ? 'bg-gradient-to-r from-blue-500 via-blue-600 to-purple-600 text-white shadow-xl transform scale-[1.02] ring-2 ring-blue-500/20'
                                  : 'text-gray-700 dark:text-gray-300 hover:bg-gradient-to-r hover:from-gray-100 hover:to-gray-50 dark:hover:from-gray-800 dark:hover:to-gray-700 hover:text-gray-900 dark:hover:text-gray-100 hover:shadow-md'
                              )}
                              title={isCollapsed ? item.label : undefined}
                            >
                              <div className={cn(
                                'flex items-center',
                                isCollapsed ? 'justify-center w-full' : 'space-x-4'
                              )}>
                                <div className={cn(
                                  'flex items-center justify-center w-8 h-8 rounded-lg transition-all duration-200 group-hover:scale-110',
                                  isActive(item.href)
                                    ? 'bg-white/20'
                                    : 'bg-gray-100/50 dark:bg-gray-700/50 group-hover:bg-blue-500/10 dark:group-hover:bg-blue-400/10'
                                )}>
                                  <item.icon className="h-4 w-4" />
                                </div>
                                {!isCollapsed && (
                                  <>
                                    <span>{item.label}</span>
                                    {'shortcut' in item && item.shortcut && (
                                      <span className="ml-auto text-xs text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity">
                                        {item.shortcut}
                                      </span>
                                    )}
                                  </>
                                )}
                              </div>
                               {!isCollapsed && 'badge' in item && item.badge && (
                                <span className={cn(
                                  "px-2.5 py-1 text-xs font-semibold rounded-full shadow-sm ring-1",
                                  isActive(item.href)
                                    ? "bg-white/20 text-white ring-white/20"
                                    : "bg-gradient-to-r from-blue-500 to-blue-600 text-white ring-blue-400/20 animate-pulse"
                                )}>
                                  {item.badge}
                                </span>
                              )}
                              {isCollapsed && isActive(item.href) && (
                                <>
                                  <div className="absolute left-0 top-1/2 transform -translate-y-1/2 w-1.5 h-8 bg-gradient-to-b from-blue-500 to-purple-600 rounded-r-full shadow-lg" />
                                  <div className="absolute inset-0 bg-gradient-to-r from-blue-500/20 to-purple-600/20 rounded-xl" />
                                </>
                              )}
                            </Link>
                          )}
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              ))}
            </nav>
          )}

          {activeTab === 'recent' && !isCollapsed && (
            <div className="p-4">
              <div className="space-y-2">
                <h3 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3">
                  Recently Accessed
                </h3>
                {recentItems.map((item) => (
                  <Link
                    key={item.id}
                    href={item.href}
                    className="flex items-center space-x-3 p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors group"
                  >
                    <div className="w-8 h-8 bg-gray-100 dark:bg-gray-800 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
                      <item.icon className="h-4 w-4 text-gray-500 dark:text-gray-400" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                        {item.label}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        {item.timestamp}
                      </p>
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          )}

        </div>

        {/* User Section */}
        <div className="p-4 border-t border-gray-200/50 dark:border-gray-700/50 bg-gradient-to-br from-gray-50/80 to-blue-50/20 dark:from-gray-800/80 dark:to-gray-700/40 backdrop-blur-sm">
          <div className="relative">
            <button
              onClick={() => setShowUserMenu(!showUserMenu)}
              className={cn(
                'w-full flex items-center p-3 rounded-xl hover:bg-white/60 dark:hover:bg-gray-700/60 transition-all duration-200 backdrop-blur-sm border border-gray-200/30 dark:border-gray-600/30 shadow-sm hover:shadow-md',
                isCollapsed ? 'justify-center' : 'space-x-4'
              )}
              title={isCollapsed ? getUserDisplayName(user) : undefined}
            >
              <div className="relative">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-600 via-purple-600 to-blue-700 rounded-full flex items-center justify-center ring-2 ring-white/50 dark:ring-gray-600/50 shadow-xl">
                  <span className="text-sm font-bold text-white">
                    {getUserInitials(user)}
                  </span>
                </div>
                <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-green-400 rounded-full border-2 border-white dark:border-gray-800 shadow-sm animate-pulse"></div>
              </div>
              {!isCollapsed && (
                <>
                  <div className="flex-1 text-left min-w-0">
                    <p className="text-sm font-semibold text-gray-900 dark:text-white truncate">
                      {getUserDisplayName(user)}
                    </p>
                    <div className="flex items-center space-x-2">
                      <p className="text-xs font-medium text-gray-600 dark:text-gray-400 truncate">
                        {user?.email || 'No email'}
                      </p>
                      {user?.role && (
                        <span className={cn(
                          "text-xs px-2 py-0.5 rounded-full font-semibold ring-1",
                          user.role === 'admin'
                            ? "bg-gradient-to-r from-red-500 to-red-600 text-white ring-red-400/20"
                            : user.role === 'user'
                            ? "bg-gradient-to-r from-blue-500 to-blue-600 text-white ring-blue-400/20"
                            : "bg-gradient-to-r from-gray-500 to-gray-600 text-white ring-gray-400/20"
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
                </>
              )}
            </button>

            {/* User Menu */}
            {showUserMenu && !isCollapsed && (
              <div className="absolute bottom-full left-0 right-0 mb-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-xl z-10">
                <div className="p-2">
                  <Link
                    href="/settings/profile"
                    onClick={() => setShowUserMenu(false)}
                    className="flex items-center space-x-3 p-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700 text-sm text-gray-700 dark:text-gray-300 transition-colors"
                  >
                    <User className="h-4 w-4" />
                    <span>Profile Settings</span>
                  </Link>
                  <Link
                    href="/settings"
                    onClick={() => setShowUserMenu(false)}
                    className="flex items-center space-x-3 p-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700 text-sm text-gray-700 dark:text-gray-300 transition-colors"
                  >
                    <Settings className="h-4 w-4" />
                    <span>Settings</span>
                  </Link>
                  <hr className="my-1 border-gray-200 dark:border-gray-700" />
                  <button
                    onClick={() => {
                      setShowUserMenu(false);
                      handleLogout();
                    }}
                    className="w-full flex items-center space-x-3 p-2 rounded-md hover:bg-red-50 dark:hover:bg-red-900/20 text-sm text-red-600 dark:text-red-400 transition-colors"
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
  isCollapsed: boolean;
}

function TopBar({ onMenuClick, isCollapsed }: TopBarProps) {
  const pathname = usePathname();
  const { stats } = useSidebarStats();
  const user = useUser();
  const [globalSearch, setGlobalSearch] = useState('');
  const [showSearch, setShowSearch] = useState(false);
  
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

  const getBreadcrumbs = () => {
    const segments = pathname.split('/').filter(Boolean);
    const breadcrumbs = [];
    
    // Only add Home if we're not already on dashboard
    if (pathname !== '/dashboard') {
      breadcrumbs.push({ label: 'Home', href: '/dashboard' });
    }
    
    let currentPath = '';
    segments.forEach((segment, index) => {
      currentPath += `/${segment}`;
      const label = segment.charAt(0).toUpperCase() + segment.slice(1).replace('-', ' ');
      breadcrumbs.push({ label, href: currentPath });
    });
    
    return breadcrumbs;
  };

  // notifications handled by NotificationBell component

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
    <header className="bg-white/95 dark:bg-gray-900/95 backdrop-blur-xl border-b border-gray-200/50 dark:border-gray-700/50 shadow-xl relative z-40">
      <div className="flex items-center justify-between px-6 py-4 min-h-[4.5rem]">
        <div className="flex items-center gap-6 flex-1 min-w-0">
          <button
            onClick={onMenuClick}
            className="lg:hidden p-3 rounded-xl hover:bg-gray-100/80 dark:hover:bg-gray-800/80 transition-all duration-200 flex-shrink-0 backdrop-blur-sm border border-gray-200/30 dark:border-gray-600/30 shadow-sm hover:shadow-md group"
          >
            <Menu className="h-5 w-5 group-hover:scale-110 transition-transform" />
          </button>
          
          {/* Enhanced Breadcrumbs */}
          <div className="hidden md:flex items-center gap-3 text-sm min-w-0 flex-1">
            <div className="flex items-center gap-2 px-3 py-2 bg-gradient-to-r from-gray-50 to-blue-50/30 dark:from-gray-800/50 dark:to-gray-700/50 rounded-xl backdrop-blur-sm border border-gray-200/30 dark:border-gray-600/30 shadow-sm">
              <Home className="h-4 w-4 text-blue-600 dark:text-blue-400 flex-shrink-0" />
              {getBreadcrumbs().map((crumb, index) => (
                <div key={`breadcrumb-${index}-${crumb.href}`} className="flex items-center gap-2 min-w-0">
                  {index > 0 && <ChevronRight className="h-3 w-3 text-gray-400 flex-shrink-0" />}
                  <Link
                    href={crumb.href}
                    className={cn(
                      'hover:text-blue-600 dark:hover:text-blue-400 transition-all duration-150 truncate px-2 py-1 rounded-lg hover:bg-white/50 dark:hover:bg-gray-700/50',
                      index === getBreadcrumbs().length - 1
                        ? 'text-gray-900 dark:text-white font-semibold bg-white/60 dark:bg-gray-700/60 shadow-sm'
                        : 'text-gray-600 dark:text-gray-400 font-medium'
                    )}
                  >
                    {crumb.label}
                  </Link>
                </div>
              ))}
            </div>
          </div>

          {/* Enhanced Mobile title */}
          <div className="md:hidden min-w-0 flex-1">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-600 via-purple-600 to-blue-700 rounded-lg flex items-center justify-center shadow-lg ring-2 ring-white/20">
                <Sparkles className="h-4 w-4 text-white" />
              </div>
              <h1 className="text-lg font-bold bg-gradient-to-r from-gray-900 to-gray-700 dark:from-white dark:to-gray-300 bg-clip-text text-transparent truncate">
                {getBreadcrumbs()[getBreadcrumbs().length - 1]?.label || 'Agentic AI'}
              </h1>
            </div>
          </div>
        </div>

        {/* Enhanced Center - Global Search */}
        <div className="hidden lg:flex flex-1 max-w-2xl mx-8">
          <div className="relative w-full group">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <Search className="h-5 w-5 text-gray-400 group-focus-within:text-blue-500 transition-colors" />
            </div>
            <input
              type="text"
              placeholder="Search agents, workflows, tools, and more..."
              value={globalSearch}
              onChange={(e) => setGlobalSearch(e.target.value)}
              className="block w-full pl-12 pr-16 py-3 border border-gray-200/50 dark:border-gray-600/50 rounded-xl bg-white/80 dark:bg-gray-800/80 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 focus:bg-white dark:focus:bg-gray-800 backdrop-blur-sm transition-all duration-200 shadow-sm focus:shadow-lg placeholder:text-gray-500"
            />
            <div className="absolute inset-y-0 right-0 pr-4 flex items-center">
              <div className="flex items-center gap-1 px-2 py-1 bg-gray-100/80 dark:bg-gray-700/80 rounded-lg text-xs text-gray-500 dark:text-gray-400 font-medium backdrop-blur-sm">
                <Command className="h-3 w-3" />
                <span>K</span>
              </div>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-4 flex-shrink-0">
          {/* Enhanced Mobile Search Toggle */}
          <button
            onClick={() => setShowSearch(!showSearch)}
            className="lg:hidden p-3 rounded-xl hover:bg-gray-100/80 dark:hover:bg-gray-800/80 transition-all duration-200 backdrop-blur-sm border border-gray-200/30 dark:border-gray-600/30 shadow-sm hover:shadow-md group"
          >
            <Search className="h-5 w-5 group-hover:scale-110 transition-transform" />
          </button>

          {/* Enhanced Quick Actions */}
          <div className="hidden md:flex items-center gap-2">
            <button
              className="p-3 rounded-xl hover:bg-gray-100/80 dark:hover:bg-gray-800/80 transition-all duration-200 backdrop-blur-sm border border-gray-200/30 dark:border-gray-600/30 shadow-sm hover:shadow-md group"
              title="Help & Documentation"
            >
              <HelpCircle className="h-5 w-5 text-gray-500 dark:text-gray-400 group-hover:text-blue-500 dark:group-hover:text-blue-400 group-hover:scale-110 transition-all" />
            </button>
            <button
              className="p-3 rounded-xl hover:bg-gray-100/80 dark:hover:bg-gray-800/80 transition-all duration-200 backdrop-blur-sm border border-gray-200/30 dark:border-gray-600/30 shadow-sm hover:shadow-md group"
              title="Bookmarks"
            >
              <Bookmark className="h-5 w-5 text-gray-500 dark:text-gray-400 group-hover:text-yellow-500 dark:group-hover:text-yellow-400 group-hover:scale-110 transition-all" />
            </button>
          </div>

          {/* Enhanced Status Indicator */}
          <div className="hidden sm:flex items-center gap-3 px-4 py-2 bg-gradient-to-r from-gray-50/80 to-blue-50/30 dark:from-gray-800/80 dark:to-gray-700/50 rounded-xl backdrop-blur-sm border border-gray-200/30 dark:border-gray-600/30 shadow-sm">
            <div className="relative">
              <div className={cn("w-3 h-3 rounded-full animate-pulse shadow-sm", getStatusColor(stats.systemHealth))}></div>
              <div className={cn("absolute inset-0 rounded-full animate-ping", getStatusColor(stats.systemHealth), "opacity-20")}></div>
            </div>
            <div className="flex flex-col">
              <span className="text-xs font-semibold text-gray-800 dark:text-gray-200 whitespace-nowrap">
                {stats.systemHealth === 'healthy' ? 'All Systems Operational' : getStatusText(stats.systemHealth)}
              </span>
              <span className="text-xs text-gray-500 dark:text-gray-400">
                System Status
              </span>
            </div>
          </div>

          {/* Notifications */}
          <div className="relative">
            {user?.id && <NotificationBell userId={user.id} />}
          </div>

          {/* Enhanced User Avatar */}
          <div className="flex items-center gap-3 p-2 rounded-xl hover:bg-gray-100/60 dark:hover:bg-gray-800/60 transition-all duration-200 backdrop-blur-sm flex-shrink-0 cursor-pointer group">
            <div className="relative">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-600 via-purple-600 to-blue-700 rounded-full flex items-center justify-center ring-2 ring-white/50 dark:ring-gray-600/50 shadow-xl group-hover:scale-105 transition-transform">
                <span className="text-sm font-bold text-white">
                  {getUserInitials(user)}
                </span>
              </div>
              <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-green-400 rounded-full border-2 border-white dark:border-gray-900 shadow-sm animate-pulse"></div>
            </div>
            {user && (
              <div className="hidden xl:block min-w-0">
                <p className="text-sm font-semibold text-gray-900 dark:text-white truncate">
                  {user.firstName && user.lastName 
                    ? `${user.firstName} ${user.lastName}`
                    : user.username || user.email?.split('@')[0] || 'User'
                  }
                </p>
                <p className="text-xs font-medium text-gray-600 dark:text-gray-400 truncate">
                  {user.role || 'User'} • Online
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Mobile Search */}
      {showSearch && (
        <div className="lg:hidden border-t border-gray-200 dark:border-gray-700 p-4">
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search className="h-4 w-4 text-gray-400" />
            </div>
            <input
              type="text"
              placeholder="Search agents, workflows, tools..."
              value={globalSearch}
              onChange={(e) => setGlobalSearch(e.target.value)}
              className="block w-full pl-10 pr-10 py-3 border border-gray-200 dark:border-gray-700 rounded-lg bg-gray-50 dark:bg-gray-800 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
              autoFocus
            />
            <button
              onClick={() => setShowSearch(false)}
              className="absolute inset-y-0 right-0 pr-3 flex items-center hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
            >
              <X className="h-4 w-4 text-gray-400" />
            </button>
          </div>
        </div>
      )}
    </header>
  );
}

export default function Navigation({ children }: { children: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const { state: authState } = useAuth();

  // Close sidebar overlay on mobile when collapsed
  useEffect(() => {
    if (sidebarCollapsed && sidebarOpen) {
      setSidebarOpen(false);
    }
  }, [sidebarCollapsed, sidebarOpen]);

  // Don't show navigation if user is not authenticated
  if (!authState.isAuthenticated) {
    return <>{children}</>;
  }

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
      <Sidebar 
        isOpen={sidebarOpen} 
        onClose={() => setSidebarOpen(false)}
        isCollapsed={sidebarCollapsed}
        onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
      />
      
      <div className="flex-1 flex flex-col overflow-hidden">
        <TopBar 
          onMenuClick={() => setSidebarOpen(true)}
          isCollapsed={sidebarCollapsed}
        />
        
        <main className="flex-1 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  );
}
