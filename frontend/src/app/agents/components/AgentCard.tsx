'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  PlayIcon, 
  PauseIcon, 
  PencilIcon, 
  TrashIcon,
  ClockIcon,
  ChartBarIcon,
  DocumentDuplicateIcon,
  CpuChipIcon,
  BoltIcon,
  EyeIcon,
  Cog6ToothIcon
} from '@heroicons/react/24/outline';
import { Agent } from '@/hooks/useAgents';

interface AgentCardProps {
  agent: Agent;
  onEdit?: (agent: Agent) => void;
  onDelete?: (agent: Agent) => void;
  onToggleStatus?: (agent: Agent) => void;
  onExecute?: (agent: Agent) => void;
  onClone?: (agent: Agent) => void;
}

const getStatusColor = (status: string): string => {
  const colors = {
    active: 'bg-green-100 text-green-800 border-green-200',
    inactive: 'bg-gray-100 text-gray-800 border-gray-200',
    error: 'bg-red-100 text-red-800 border-red-200',
    draft: 'bg-yellow-100 text-yellow-800 border-yellow-200',
  };
  return colors[status as keyof typeof colors] || colors.inactive;
};

const getFrameworkIcon = (framework: string): { icon: string; color: string } => {
  const frameworks = {
    langgraph: { icon: '⚡', color: 'from-purple-500 to-purple-700' },
    crewai: { icon: '👥', color: 'from-blue-500 to-blue-700' },
    autogen: { icon: '🔄', color: 'from-green-500 to-green-700' },
    semantic_kernel: { icon: '🧠', color: 'from-orange-500 to-orange-700' },
    custom: { icon: '⚙️', color: 'from-gray-500 to-gray-700' },
    langchain: { icon: '🦜', color: 'from-teal-500 to-teal-700' },
    llamaindex: { icon: '🦙', color: 'from-indigo-500 to-indigo-700' },
  };
  return frameworks[framework as keyof typeof frameworks] || { icon: '🤖', color: 'from-gray-500 to-gray-700' };
};

const formatRelativeTime = (date: Date): string => {
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (diffInSeconds < 60) return 'just now';
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
  return `${Math.floor(diffInSeconds / 86400)}d ago`;
};

export function AgentCard({ 
  agent, 
  onEdit, 
  onDelete, 
  onToggleStatus, 
  onExecute,
  onClone
}: AgentCardProps) {
  const [isHovered, setIsHovered] = useState(false);
  const frameworkData = getFrameworkIcon(agent.framework);

  return (
    <Card 
      className="group relative overflow-hidden transition-all duration-300 hover:shadow-2xl hover:shadow-blue-500/10 border border-gray-200/50 dark:border-gray-700/50 bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl hover:scale-[1.02]"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Gradient Background */}
      <div className={`absolute inset-0 bg-gradient-to-br ${frameworkData.color} opacity-0 group-hover:opacity-5 transition-opacity duration-300`} />
      
      {/* Status Indicator Strip */}
      <div className={`absolute top-0 left-0 right-0 h-1 bg-gradient-to-r ${
        agent.status === 'active' ? 'from-emerald-400 to-emerald-600' :
        agent.status === 'error' ? 'from-red-400 to-red-600' :
        agent.status === 'draft' ? 'from-amber-400 to-amber-600' :
        'from-gray-300 to-gray-500'
      }`} />

      <CardHeader className="pb-4 relative">
        {/* Header with Icon and Actions */}
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-4">
            {/* Framework Icon with Gradient Background */}
            <div className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${frameworkData.color} flex items-center justify-center text-2xl shadow-lg transform group-hover:scale-110 transition-transform duration-200`}>
              {frameworkData.icon}
            </div>
            
            <div className="space-y-1">
              <CardTitle className="text-xl font-bold text-gray-900 dark:text-white tracking-tight">
                {agent.name}
              </CardTitle>
              
              <div className="flex items-center gap-3">
                <Badge
                  className={`text-xs font-semibold px-2.5 py-1 rounded-full ${getStatusColor(agent.status)}`}
                >
                  <div className={`w-1.5 h-1.5 rounded-full mr-1.5 ${
                    agent.status === 'active' ? 'bg-green-500' :
                    agent.status === 'error' ? 'bg-red-500' :
                    agent.status === 'draft' ? 'bg-amber-500' :
                    'bg-gray-400'
                  }`} />
                  {agent.status.toUpperCase()}
                </Badge>
                
                <div className="flex items-center gap-1 text-xs text-gray-500">
                  <CpuChipIcon className="w-3 h-3" />
                  {agent.framework}
                </div>
              </div>
            </div>
          </div>
          
          {/* Hover Actions */}
          <div className={`flex gap-1 transition-all duration-200 ${
            isHovered ? 'opacity-100 translate-x-0' : 'opacity-0 translate-x-4'
          }`}>
            <Button
              size="icon"
              variant="ghost"
              onClick={() => onExecute?.(agent)}
              className="h-9 w-9 rounded-xl hover:bg-emerald-50 hover:text-emerald-600 dark:hover:bg-emerald-950"
            >
              <BoltIcon className="h-4 w-4" />
            </Button>
            <Button
              size="icon"
              variant="ghost"
              onClick={() => onEdit?.(agent)}
              className="h-9 w-9 rounded-xl hover:bg-blue-50 hover:text-blue-600 dark:hover:bg-blue-950"
            >
              <Cog6ToothIcon className="h-4 w-4" />
            </Button>
            <Button
              size="icon"
              variant="ghost"
              onClick={() => onClone?.(agent)}
              className="h-9 w-9 rounded-xl hover:bg-purple-50 hover:text-purple-600 dark:hover:bg-purple-950"
            >
              <DocumentDuplicateIcon className="h-4 w-4" />
            </Button>
          </div>
        </div>
        
        {/* Description */}
        <CardDescription className="text-sm text-gray-600 dark:text-gray-300 mt-3 line-clamp-2 leading-relaxed">
          {agent.description}
        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-6 relative">
        {/* Performance Metrics */}
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center p-3 rounded-xl bg-gray-50/50 dark:bg-gray-800/50 border border-gray-100 dark:border-gray-700">
            <div className="text-lg font-bold text-gray-900 dark:text-white">
              {agent.performance?.tasksCompleted || 0}
            </div>
            <div className="text-xs text-gray-500 mt-1">Tasks</div>
          </div>
          
          <div className="text-center p-3 rounded-xl bg-gray-50/50 dark:bg-gray-800/50 border border-gray-100 dark:border-gray-700">
            <div className="text-lg font-bold text-emerald-600 dark:text-emerald-400">
              {agent.performance?.successRate || 0}%
            </div>
            <div className="text-xs text-gray-500 mt-1">Success</div>
          </div>
          
          <div className="text-center p-3 rounded-xl bg-gray-50/50 dark:bg-gray-800/50 border border-gray-100 dark:border-gray-700">
            <div className="text-lg font-bold text-blue-600 dark:text-blue-400">
              {Math.round(agent.performance?.avgResponseTime || 0)}ms
            </div>
            <div className="text-xs text-gray-500 mt-1">Avg Time</div>
          </div>
        </div>

        {/* Capabilities */}
        {agent.capabilities?.length > 0 && (
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 dark:text-gray-300">
              <BoltIcon className="w-4 h-4" />
              Capabilities
            </div>
            <div className="flex flex-wrap gap-2">
              {agent.capabilities.slice(0, 4).map((capability: string, index) => (
                <Badge 
                  key={capability} 
                  variant="secondary" 
                  className="text-xs font-medium px-3 py-1 rounded-full bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 text-blue-700 dark:text-blue-300 border-0"
                >
                  {capability}
                </Badge>
              ))}
              {agent.capabilities.length > 4 && (
                <Badge variant="outline" className="text-xs rounded-full">
                  +{agent.capabilities.length - 4}
                </Badge>
              )}
            </div>
          </div>
        )}

        {/* Tags */}
        {agent.tags?.length > 0 && (
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 dark:text-gray-300">
              <EyeIcon className="w-4 h-4" />
              Tags
            </div>
            <div className="flex flex-wrap gap-2">
              {agent.tags.slice(0, 3).map((tag) => (
                <Badge 
                  key={tag} 
                  variant="outline" 
                  className="text-xs rounded-full border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-400"
                >
                  #{tag}
                </Badge>
              ))}
              {agent.tags.length > 3 && (
                <Badge variant="outline" className="text-xs rounded-full">
                  +{agent.tags.length - 3}
                </Badge>
              )}
            </div>
          </div>
        )}

        {/* Footer Actions */}
        <div className="flex items-center justify-between pt-4 border-t border-gray-100/50 dark:border-gray-700/50">
          <div className="flex items-center gap-2 text-xs text-gray-500">
            <ClockIcon className="w-3 h-3" />
            Updated {formatRelativeTime(new Date(agent.updated_at))}
          </div>
          
          <div className="flex gap-2">
            {onToggleStatus && (
              <Button
                size="sm"
                variant={agent.status === 'active' ? 'outline' : 'default'}
                onClick={() => onToggleStatus(agent)}
                className="h-8 px-3 text-xs rounded-lg font-medium"
              >
                {agent.status === 'active' ? (
                  <>
                    <PauseIcon className="h-3 w-3 mr-1.5" />
                    Pause
                  </>
                ) : (
                  <>
                    <PlayIcon className="h-3 w-3 mr-1.5" />
                    Activate
                  </>
                )}
              </Button>
            )}
            
            {onDelete && (
              <Button
                size="sm"
                variant="destructive"
                onClick={() => onDelete(agent)}
                className="h-8 w-8 p-0 rounded-lg"
              >
                <TrashIcon className="h-3 w-3" />
              </Button>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
