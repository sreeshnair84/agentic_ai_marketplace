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
  TestTube
} from 'lucide-react';
import { cn } from '@/lib/utils';

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
    id: 'main',
    label: 'Main',
    items: [
      {
        id: 'dashboard',
        label: 'Dashboard',
        href: '/dashboard',
        icon: LayoutDashboard,
        shortcut: '⌘D'
      },
      {
        id: 'projects',
        label: 'Projects',
        href: '/projects',
        icon: FolderOpen,
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
        label: 'Chat Interface',
        href: '/chat',
        icon: MessageSquare,
        shortcut: '⌘C'
      },
      {
        id: 'agents',
        label: 'Agents',
        href: '/agents',
        icon: Bot,
        children: [
          {
            id: 'agents-active',
            label: 'Active Agents',
            href: '/agents?status=active',
            icon: TrendingUp
          },
          {
            id: 'agents-templates',
            label: 'Agent Templates',
            href: '/agents/templates',
            icon: Star
          }
        ]
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
        icon: Zap,
        children: [
          {
            id: 'tools-templates',
            label: 'Tool Templates',
            href: '/templates/tools',
            icon: Star
          }
        ]
      },
      {
        id: 'mcp',
        label: 'MCP Management',
        href: '/mcp',
        icon: Command,
        children: [
          {
            id: 'mcp-servers',
            label: 'MCP Servers',
            href: '/mcp?tab=servers',
            icon: Bot
          },
          {
            id: 'mcp-endpoints',
            label: 'Gateway Endpoints',
            href: '/mcp?tab=endpoints',
            icon: Zap
          },
          {
            id: 'mcp-tools',
            label: 'Discovered Tools',
            href: '/mcp?tab=tools',
            icon: Command
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

  const filteredNavigation = getNavigationWithBadges().map(section => ({
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
          'fixed top-0 left-0 z-50 h-full bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700 transform transition-all duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0 flex flex-col',
          isCollapsed ? 'w-16' : 'w-64',
          isOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        {/* Header */}
        <div className={cn(
          'flex items-center border-b border-gray-200 dark:border-gray-700 p-4 min-h-[4rem]',
          isCollapsed ? 'justify-center px-2' : 'justify-between'
        )}>
          {!isCollapsed && (
            <div className="flex items-center gap-3 min-w-0 flex-1">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center shadow-lg flex-shrink-0">
                <Bot className="h-5 w-5 text-white" />
              </div>
              <div className="min-w-0 flex-1">
                <h2 className="font-bold text-lg text-gray-900 dark:text-white truncate">
                  Agentic AI
                </h2>
                <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                  Multi-Agent Platform
                </p>
              </div>
            </div>
          )}
          {isCollapsed && (
            <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center shadow-lg">
              <Bot className="h-5 w-5 text-white" />
            </div>
          )}
          <div className="flex items-center gap-1 flex-shrink-0">
            <button
              onClick={onToggleCollapse}
              className="hidden lg:flex p-1.5 rounded-md hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
              title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
            >
              {isCollapsed ? <Maximize2 className="h-4 w-4" /> : <Minimize2 className="h-4 w-4" />}
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
          <div className="p-4 border-b border-gray-200 dark:border-gray-700 space-y-3">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400 flex-shrink-0" />
              <input
                type="text"
                placeholder="Search..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-10 py-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
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
            <div className="grid grid-cols-3 gap-2">
              {quickActions.map((action) => (
                <Link
                  key={action.id}
                  href={action.href}
                  className="flex flex-col items-center p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors group"
                  title={action.label}
                >
                  <div className={cn(
                    "w-8 h-8 rounded-lg flex items-center justify-center mb-1 group-hover:scale-110 transition-transform",
                    action.color
                  )}>
                    <action.icon className="h-4 w-4 text-white" />
                  </div>
                  <span className="text-xs text-gray-600 dark:text-gray-400 text-center leading-tight">
                    {action.label.split(' ')[1] || action.label}
                  </span>
                </Link>
              ))}
            </div>
          </div>
        )}

        {/* Project Selector */}
        {!isCollapsed && (
          <div className="p-4 border-b border-gray-200 dark:border-gray-700">
            <div className="relative">
              <button
                onClick={() => setShowProjectDropdown(!showProjectDropdown)}
                className="w-full flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors min-h-[3.5rem]"
              >
                <div className="flex items-center gap-3 min-w-0 flex-1">
                  {state.selectedProject ? (
                    <>
                      <div 
                        className="w-3 h-3 rounded-full flex-shrink-0"
                        style={{ backgroundColor: state.selectedProject.color }}
                      />
                      <div className="text-left min-w-0 flex-1">
                        <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                          {state.selectedProject.name}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                          {state.selectedProject.tags.slice(0, 2).join(', ')}
                          {state.selectedProject.tags.length > 2 && '...'}
                        </p>
                      </div>
                    </>
                  ) : (
                    <>
                      <FolderOpen className="w-4 h-4 text-gray-400 flex-shrink-0" />
                      <div className="text-left min-w-0 flex-1">
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
                  "h-4 w-4 text-gray-400 transition-transform flex-shrink-0",
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
        )}

        {/* Navigation Tabs */}
        {!isCollapsed && (
          <div className="flex border-b border-gray-200 dark:border-gray-700">
            {[
              { id: 'nav', label: 'Navigation', icon: Menu },
              { id: 'recent', label: 'Recent', icon: Clock },
              { id: 'bookmarks', label: 'Bookmarks', icon: Bookmark }
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
                ? [{ id: 'search-results', label: 'Search Results', items: filteredNavigation.flatMap(s => s.items) } as NavigationSection] 
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
                          {item.children && !isCollapsed ? (
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
                                'flex items-center justify-between px-3 py-2 rounded-lg text-sm font-medium transition-all group relative',
                                isActive(item.href)
                                  ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg transform scale-105'
                                  : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-gray-100'
                              )}
                              title={isCollapsed ? item.label : undefined}
                            >
                              <div className={cn(
                                'flex items-center',
                                isCollapsed ? 'justify-center w-full' : 'space-x-3'
                              )}>
                                <item.icon className="h-4 w-4 group-hover:scale-110 transition-transform" />
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
                              {!isCollapsed && item.badge && (
                                <span className={cn(
                                  "px-2 py-0.5 text-xs rounded-full",
                                  isActive(item.href)
                                    ? "bg-white/20 text-white"
                                    : "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300"
                                )}>
                                  {item.badge}
                                </span>
                              )}
                              {isCollapsed && isActive(item.href) && (
                                <div className="absolute left-0 top-1/2 transform -translate-y-1/2 w-1 h-6 bg-white rounded-r-full" />
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
        <div className="p-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50">
          <div className="relative">
            <button
              onClick={() => setShowUserMenu(!showUserMenu)}
              className={cn(
                'w-full flex items-center p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors',
                isCollapsed ? 'justify-center' : 'space-x-3'
              )}
              title={isCollapsed ? getUserDisplayName(user) : undefined}
            >
              <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-full flex items-center justify-center ring-2 ring-white dark:ring-gray-800 shadow-lg">
                <span className="text-sm font-medium text-white">
                  {getUserInitials(user)}
                </span>
              </div>
              {!isCollapsed && (
                <>
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
                          "text-xs px-1.5 py-0.5 rounded font-medium",
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
  const [showNotifications, setShowNotifications] = useState(false);
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

  const notifications = [
    {
      id: '1',
      type: 'success',
      title: 'Agent Deployed',
      message: 'Customer Support Agent is now live',
      time: '2 min ago',
      unread: true
    },
    {
      id: '2',
      type: 'warning',
      title: 'High CPU Usage',
      message: 'RAG Service using 85% CPU',
      time: '5 min ago',
      unread: true
    },
    {
      id: '3',
      type: 'info',
      title: 'Workflow Completed',
      message: 'Invoice processing workflow finished',
      time: '10 min ago',
      unread: false
    }
  ];

  const unreadCount = notifications.filter(n => n.unread).length;

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
    <header className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 shadow-sm relative z-40">
      <div className="flex items-center justify-between px-4 py-3 min-h-[4rem]">
        <div className="flex items-center gap-4 flex-1 min-w-0">
          <button
            onClick={onMenuClick}
            className="lg:hidden p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors flex-shrink-0"
          >
            <Menu className="h-5 w-5" />
          </button>
          
          {/* Breadcrumbs */}
          <div className="hidden md:flex items-center gap-2 text-sm min-w-0 flex-1">
            {getBreadcrumbs().map((crumb, index) => (
              <div key={`breadcrumb-${index}-${crumb.href}`} className="flex items-center gap-2 min-w-0">
                {index > 0 && <ChevronRight className="h-4 w-4 text-gray-400 flex-shrink-0" />}
                <Link
                  href={crumb.href}
                  className={cn(
                    'hover:text-blue-600 dark:hover:text-blue-400 transition-colors truncate',
                    index === getBreadcrumbs().length - 1
                      ? 'text-gray-900 dark:text-white font-medium'
                      : 'text-gray-500 dark:text-gray-400'
                  )}
                >
                  {crumb.label}
                </Link>
              </div>
            ))}
          </div>

          {/* Mobile title */}
          <div className="md:hidden min-w-0 flex-1">
            <h1 className="text-lg font-semibold text-gray-900 dark:text-white truncate">
              {getBreadcrumbs()[getBreadcrumbs().length - 1]?.label || 'Platform'}
            </h1>
          </div>
        </div>

        {/* Center - Global Search */}
        <div className="hidden lg:flex flex-1 max-w-lg mx-8">
          <div className="relative w-full">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search className="h-4 w-4 text-gray-400" />
            </div>
            <input
              type="text"
              placeholder="Search agents, workflows, tools..."
              value={globalSearch}
              onChange={(e) => setGlobalSearch(e.target.value)}
              className="block w-full pl-10 pr-12 py-2 border border-gray-200 dark:border-gray-700 rounded-lg bg-gray-50 dark:bg-gray-800 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
            />
            <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
              <div className="flex items-center gap-1 text-xs text-gray-400">
                <Command className="h-3 w-3" />
                <span>K</span>
              </div>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3 flex-shrink-0">
          {/* Mobile Search Toggle */}
          <button
            onClick={() => setShowSearch(!showSearch)}
            className="lg:hidden p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
          >
            <Search className="h-5 w-5" />
          </button>

          {/* Quick Actions */}
          <div className="hidden md:flex items-center gap-1">
            <button
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
              title="Help"
            >
              <HelpCircle className="h-5 w-5 text-gray-500 dark:text-gray-400" />
            </button>
          </div>

          {/* Status Indicator */}
          <div className="hidden sm:flex items-center gap-2 px-3 py-1 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <div className={cn("w-2 h-2 rounded-full animate-pulse", getStatusColor(stats.systemHealth))}></div>
            <span className="text-xs font-medium text-gray-600 dark:text-gray-400 whitespace-nowrap">
              {stats.systemHealth === 'healthy' ? 'Operational' : getStatusText(stats.systemHealth)}
            </span>
          </div>

          {/* Notifications */}
          <div className="relative">
            <button
              onClick={() => setShowNotifications(!showNotifications)}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors relative"
            >
              <Bell className="h-5 w-5 text-gray-500 dark:text-gray-400" />
              {unreadCount > 0 && (
                <span className="absolute -top-0.5 -right-0.5 h-4 w-4 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
                  {unreadCount}
                </span>
              )}
            </button>

            {/* Notifications Dropdown */}
            {showNotifications && (
              <div className="absolute top-full right-0 mt-2 w-80 max-w-[calc(100vw-2rem)] bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-xl z-50">
                <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                  <div className="flex items-center justify-between">
                    <h3 className="text-sm font-semibold text-gray-900 dark:text-white">
                      Notifications
                    </h3>
                    <button className="text-xs text-blue-600 dark:text-blue-400 hover:underline transition-colors">
                      Mark all as read
                    </button>
                  </div>
                </div>
                <div className="max-h-96 overflow-y-auto">
                  {notifications.map((notification) => (
                    <div
                      key={notification.id}
                      className={cn(
                        'p-4 border-b border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors',
                        notification.unread && 'bg-blue-50 dark:bg-blue-900/20'
                      )}
                    >
                      <div className="flex items-start gap-3">
                        <div className={cn(
                          'w-2 h-2 rounded-full mt-2 flex-shrink-0',
                          notification.type === 'success' && 'bg-green-500',
                          notification.type === 'warning' && 'bg-yellow-500',
                          notification.type === 'info' && 'bg-blue-500'
                        )} />
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                            {notification.title}
                          </p>
                          <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-2">
                            {notification.message}
                          </p>
                          <p className="text-xs text-gray-400 mt-1">
                            {notification.time}
                          </p>
                        </div>
                        {notification.unread && (
                          <div className="w-2 h-2 bg-blue-500 rounded-full flex-shrink-0" />
                        )}
                      </div>
                    </div>
                  ))}
                </div>
                <div className="p-3 border-t border-gray-200 dark:border-gray-700">
                  <Link
                    href="/notifications"
                    className="text-xs text-blue-600 dark:text-blue-400 hover:underline"
                    onClick={() => setShowNotifications(false)}
                  >
                    View all notifications
                  </Link>
                </div>
              </div>
            )}
          </div>

          {/* User Avatar */}
          <div className="flex items-center gap-2 flex-shrink-0">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-full flex items-center justify-center ring-2 ring-white dark:ring-gray-900 shadow-lg">
              <span className="text-sm font-medium text-white">
                {getUserInitials(user)}
              </span>
            </div>
            {user && (
              <div className="hidden xl:block min-w-0">
                <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                  {user.firstName && user.lastName 
                    ? `${user.firstName} ${user.lastName}`
                    : user.username || user.email?.split('@')[0] || 'User'
                  }
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                  {user.role || 'User'}
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
