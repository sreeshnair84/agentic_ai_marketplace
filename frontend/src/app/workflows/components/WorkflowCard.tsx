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
  UserGroupIcon,
  CpuChipIcon,
  BoltIcon,
  EyeIcon,
  Cog6ToothIcon,
  BeakerIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline';
import {
  PlayIcon as PlayIconSolid,
  PauseIcon as PauseIconSolid,
  CheckCircleIcon as CheckCircleIconSolid,
  ExclamationTriangleIcon as ExclamationTriangleIconSolid
} from '@heroicons/react/24/solid';
import { type WorkflowData } from '@/hooks/useWorkflows';

interface WorkflowCardProps {
  workflow: WorkflowData;
  onEdit?: (workflow: WorkflowData) => void;
  onDelete?: (workflow: WorkflowData) => void;
  onExecute?: (workflow: WorkflowData) => void;
  onClone?: (workflow: WorkflowData) => void;
  onPause?: (workflow: WorkflowData) => void;
  onResume?: (workflow: WorkflowData) => void;
}

const getComplexityData = (complexity: string): { color: string; icon: string } => {
  const complexityMap = {
    simple: { color: 'from-emerald-400 to-emerald-600', icon: '🎯' },
    moderate: { color: 'from-amber-400 to-amber-600', icon: '⚡' },
    complex: { color: 'from-red-400 to-red-600', icon: '🧠' },
  };
  return complexityMap[complexity as keyof typeof complexityMap] || { color: 'from-gray-400 to-gray-600', icon: '⚙️' };
};

const getCategoryData = (category: string): { color: string; icon: string } => {
  const categoryMap = {
    automation: { color: 'from-blue-500 to-blue-700', icon: '🔄' },
    'data-processing': { color: 'from-purple-500 to-purple-700', icon: '📊' },
    'ai-pipeline': { color: 'from-pink-500 to-pink-700', icon: '🤖' },
    integration: { color: 'from-teal-500 to-teal-700', icon: '🔗' },
    monitoring: { color: 'from-orange-500 to-orange-700', icon: '📈' },
  };
  return categoryMap[category as keyof typeof categoryMap] || { color: 'from-gray-500 to-gray-700', icon: '⚙️' };
};

const formatRelativeTime = (date: Date | string): string => {
  const now = new Date();
  const targetDate = typeof date === 'string' ? new Date(date) : date;
  const diffInSeconds = Math.floor((now.getTime() - targetDate.getTime()) / 1000);

  if (diffInSeconds < 60) return 'just now';
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
  return `${Math.floor(diffInSeconds / 86400)}d ago`;
};

export function WorkflowCard({
  workflow,
  onEdit,
  onDelete,
  onExecute,
  onClone,
  onPause,
  onResume
}: WorkflowCardProps) {
  const [isHovered, setIsHovered] = useState(false);
  const complexityData = getComplexityData(workflow.complexity);
  const categoryData = getCategoryData(workflow.category);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <CheckCircleIconSolid className="w-5 h-5 text-emerald-500" />;
      case 'running':
        return <PlayIconSolid className="w-5 h-5 text-blue-500" />;
      case 'inactive':
        return <PauseIconSolid className="w-5 h-5 text-gray-400" />;
      case 'error':
        return <ExclamationTriangleIconSolid className="w-5 h-5 text-red-500" />;
      case 'draft':
        return <BeakerIcon className="w-5 h-5 text-amber-500" />;
      default:
        return <CheckCircleIcon className="w-5 h-5 text-gray-400" />;
    }
  };

  const successRate = workflow.execution.totalRuns > 0 
    ? (workflow.execution.successfulRuns / workflow.execution.totalRuns) * 100 
    : 0;

  // Ensure triggers is always an array to avoid TS "possibly undefined" errors
  const triggers = workflow.schedule?.triggers ?? [];

  return (
    <Card 
      className="group relative overflow-hidden transition-all duration-300 hover:shadow-2xl hover:shadow-blue-500/10 border border-gray-200/50 dark:border-gray-700/50 bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl hover:scale-[1.02]"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Gradient Background */}
      <div className={`absolute inset-0 bg-gradient-to-br ${categoryData.color} opacity-0 group-hover:opacity-5 transition-opacity duration-300`} />
      
      {/* Status Indicator Strip */}
      <div className={`absolute top-0 left-0 right-0 h-1 bg-gradient-to-r ${
        workflow.status === 'active' ? 'from-emerald-400 to-emerald-600' :
        workflow.status === 'running' ? 'from-blue-400 to-blue-600' :
        workflow.status === 'error' ? 'from-red-400 to-red-600' :
        workflow.status === 'draft' ? 'from-amber-400 to-amber-600' :
        'from-gray-300 to-gray-500'
      }`} />

      <CardHeader className="pb-4 relative">
        {/* Header with Icon and Actions */}
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-4">
            {/* Category Icon with Gradient Background */}
            <div className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${categoryData.color} flex items-center justify-center text-2xl shadow-lg transform group-hover:scale-110 transition-transform duration-200`}>
              {categoryData.icon}
            </div>
            
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                {getStatusIcon(workflow.status)}
                <CardTitle className="text-xl font-bold text-gray-900 dark:text-white tracking-tight">
                  {workflow.name}
                </CardTitle>
              </div>
              
              <div className="flex items-center gap-3">
                <Badge className={`text-xs font-semibold px-3 py-1 rounded-full ${
                  workflow.status === 'active' ? 'bg-emerald-100 text-emerald-800 border-emerald-200 dark:bg-emerald-900/20 dark:text-emerald-300' :
                  workflow.status === 'running' ? 'bg-blue-100 text-blue-800 border-blue-200 dark:bg-blue-900/20 dark:text-blue-300' :
                  workflow.status === 'error' ? 'bg-red-100 text-red-800 border-red-200 dark:bg-red-900/20 dark:text-red-300' :
                  workflow.status === 'draft' ? 'bg-amber-100 text-amber-800 border-amber-200 dark:bg-amber-900/20 dark:text-amber-300' :
                  'bg-gray-100 text-gray-800 border-gray-200 dark:bg-gray-900/20 dark:text-gray-300'
                }`}>
                  {workflow.status.toUpperCase()}
                </Badge>
                
                <Badge className={`text-xs font-medium px-3 py-1 rounded-full ${
                  workflow.complexity === 'simple' ? 'bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-900/20' :
                  workflow.complexity === 'moderate' ? 'bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-900/20' :
                  'bg-red-50 text-red-700 border-red-200 dark:bg-red-900/20'
                }`}>
                  {complexityData.icon} {workflow.complexity}
                </Badge>
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
              onClick={() => onExecute?.(workflow)}
              disabled={workflow.status === 'error' || workflow.status === 'draft'}
              className="h-9 w-9 rounded-xl hover:bg-emerald-50 hover:text-emerald-600 dark:hover:bg-emerald-950"
            >
              <BoltIcon className="h-4 w-4" />
            </Button>
            <Button
              size="icon"
              variant="ghost"
              onClick={() => onEdit?.(workflow)}
              className="h-9 w-9 rounded-xl hover:bg-blue-50 hover:text-blue-600 dark:hover:bg-blue-950"
            >
              <Cog6ToothIcon className="h-4 w-4" />
            </Button>
            <Button
              size="icon"
              variant="ghost"
              onClick={() => onClone?.(workflow)}
              className="h-9 w-9 rounded-xl hover:bg-purple-50 hover:text-purple-600 dark:hover:bg-purple-950"
            >
              <DocumentDuplicateIcon className="h-4 w-4" />
            </Button>
          </div>
        </div>
        
        {/* Description */}
        <CardDescription className="text-sm text-gray-600 dark:text-gray-300 mt-3 line-clamp-2 leading-relaxed">
          {workflow.description}
        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-6 relative">
        {/* Performance Metrics */}
        <div className="grid grid-cols-4 gap-3">
          <div className="text-center p-3 rounded-xl bg-gray-50/50 dark:bg-gray-800/50 border border-gray-100 dark:border-gray-700">
            <div className="text-lg font-bold text-gray-900 dark:text-white">
              {workflow.execution.totalRuns}
            </div>
            <div className="text-xs text-gray-500 mt-1">Runs</div>
          </div>
          
          <div className="text-center p-3 rounded-xl bg-gray-50/50 dark:bg-gray-800/50 border border-gray-100 dark:border-gray-700">
            <div className="text-lg font-bold text-emerald-600 dark:text-emerald-400">
              {Math.round(successRate)}%
            </div>
            <div className="text-xs text-gray-500 mt-1">Success</div>
          </div>
          
          <div className="text-center p-3 rounded-xl bg-gray-50/50 dark:bg-gray-800/50 border border-gray-100 dark:border-gray-700">
            <div className="text-lg font-bold text-blue-600 dark:text-blue-400">
              {workflow.execution.avgDuration}s
            </div>
            <div className="text-xs text-gray-500 mt-1">Avg Time</div>
          </div>

          <div className="text-center p-3 rounded-xl bg-gray-50/50 dark:bg-gray-800/50 border border-gray-100 dark:border-gray-700">
            <div className="text-lg font-bold text-purple-600 dark:text-purple-400">
              {workflow.agents.length}
            </div>
            <div className="text-xs text-gray-500 mt-1">Agents</div>
          </div>
        </div>

        {/* Agents */}
        {workflow.agents?.length > 0 && (
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 dark:text-gray-300">
              <UserGroupIcon className="w-4 h-4" />
              Connected Agents ({workflow.agents.length})
            </div>
            <div className="flex flex-wrap gap-2">
              {workflow.agents.slice(0, 3).map((agent) => (
                <Badge 
                  key={agent.id} 
                  variant="secondary" 
                  className="text-xs font-medium px-3 py-1 rounded-full bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 text-blue-700 dark:text-blue-300 border-0 flex items-center gap-1"
                >
                  <UserGroupIcon className="w-3 h-3" />
                  {agent.name}
                </Badge>
              ))}
              {workflow.agents.length > 3 && (
                <Badge variant="outline" className="text-xs rounded-full">
                  +{workflow.agents.length - 3} more
                </Badge>
              )}
            </div>
          </div>
        )}

        {/* Tools */}
        {workflow.tools?.length > 0 && (
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 dark:text-gray-300">
              <CpuChipIcon className="w-4 h-4" />
              Tools ({workflow.tools.length})
            </div>
            <div className="flex flex-wrap gap-2">
              {workflow.tools.slice(0, 3).map((tool) => (
                <Badge 
                  key={tool.id} 
                  variant="outline" 
                  className="text-xs rounded-full border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-400 flex items-center gap-1"
                >
                  <CpuChipIcon className="w-3 h-3" />
                  {tool.name}
                </Badge>
              ))}
              {workflow.tools.length > 3 && (
                <Badge variant="outline" className="text-xs rounded-full">
                  +{workflow.tools.length - 3} more
                </Badge>
              )}
            </div>
          </div>
        )}

        {/* Triggers */}
  {triggers.length > 0 && (
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 dark:text-gray-300">
              <ClockIcon className="w-4 h-4" />
              Triggers
            </div>
            <div className="flex flex-wrap gap-2">
              {triggers.slice(0, 2).map((trigger: string, index: number) => (
                <Badge 
                  key={index} 
                  variant="outline" 
                  className="text-xs rounded-full border-amber-300 dark:border-amber-600 text-amber-600 dark:text-amber-400"
                >
                  {trigger}
                </Badge>
              ))}
              {triggers.length > 2 && (
                <Badge variant="outline" className="text-xs rounded-full">
                  +{triggers.length - 2} more
                </Badge>
              )}
            </div>
          </div>
        )}

        {/* Footer Actions */}
        <div className="flex items-center justify-between pt-4 border-t border-gray-100/50 dark:border-gray-700/50">
          <div className="flex items-center gap-2 text-xs text-gray-500">
            <ClockIcon className="w-3 h-3" />
            Updated {formatRelativeTime(workflow.updated_at)}
          </div>
          
          <div className="flex gap-2">
            {workflow.status === 'running' ? (
              <Button
                size="sm"
                variant="outline"
                onClick={() => onPause?.(workflow)}
                className="h-8 px-3 text-xs rounded-lg font-medium"
              >
                <PauseIcon className="h-3 w-3 mr-1.5" />
                Pause
              </Button>
            ) : (
              <Button
                size="sm"
                variant={workflow.status === 'active' ? 'default' : 'outline'}
                onClick={() => onExecute?.(workflow)}
                disabled={workflow.status === 'error' || workflow.status === 'draft'}
                className="h-8 px-3 text-xs rounded-lg font-medium"
              >
                <PlayIcon className="h-3 w-3 mr-1.5" />
                Run
              </Button>
            )}
            
            <Button
              size="sm"
              variant="ghost"
              onClick={() => onDelete?.(workflow)}
              className="h-8 w-8 p-0 rounded-lg hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-950"
            >
              <TrashIcon className="h-3 w-3" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}