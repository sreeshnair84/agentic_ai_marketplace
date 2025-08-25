import React from "react";
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
  Cog6ToothIcon,
  BeakerIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ArrowPathIcon,
  CloudIcon,
  ServerIcon,
  ComputerDesktopIcon,
  CodeBracketIcon,
  WrenchScrewdriverIcon
} from '@heroicons/react/24/outline';
import {
  CheckCircleIcon as CheckCircleIconSolid,
  ExclamationTriangleIcon as ExclamationTriangleIconSolid,
  CloudIcon as CloudIconSolid
} from '@heroicons/react/24/solid';

interface BaseToolData {
  id: string;
  name?: string;
  display_name: string;
  description: string;
  created_at: string;
  updated_at: string;
}

interface ToolTemplate extends BaseToolData {
  category: string;
  complexity?: 'simple' | 'moderate' | 'complex';
  fields?: Array<{
    id: string;
    field_name: string;
    field_label: string;
    field_type: string;
    is_required: boolean;
  }>;
}

interface ToolInstance extends BaseToolData {
  template_name?: string;
  status: 'active' | 'inactive' | 'error' | 'testing';
  environment_scope: 'local' | 'cloud' | 'hybrid';
  configuration?: Record<string, any>;
  performance?: {
    averageResponseTime?: number;
    successRate?: number;
    totalRequests?: number;
  };
}

interface ToolCardProps {
  tool: ToolTemplate | ToolInstance;
  type: 'template' | 'instance';
  onEdit?: (tool: ToolTemplate | ToolInstance) => void;
  onDelete?: (tool: ToolTemplate | ToolInstance) => void;
  onTest?: (tool: ToolInstance) => void;
  onClone?: (tool: ToolTemplate | ToolInstance) => void;
  onToggleStatus?: (tool: ToolInstance) => void;
  onManage?: (tool: ToolInstance) => void;
}

const getCategoryData = (category: string): { color: string; icon: string } => {
  const categoryMap = {
    'data-processing': { color: 'from-blue-500 to-blue-700', icon: '📊' },
    'ai-ml': { color: 'from-purple-500 to-purple-700', icon: '🤖' },
    'web-scraping': { color: 'from-green-500 to-green-700', icon: '🕷️' },
    'api-integration': { color: 'from-orange-500 to-orange-700', icon: '🔌' },
    'database': { color: 'from-red-500 to-red-700', icon: '🗄️' },
    'utility': { color: 'from-teal-500 to-teal-700', icon: '🛠️' },
    'communication': { color: 'from-pink-500 to-pink-700', icon: '💬' },
    'security': { color: 'from-indigo-500 to-indigo-700', icon: '🔒' },
    'monitoring': { color: 'from-amber-500 to-amber-700', icon: '📈' },
  };
  return categoryMap[category as keyof typeof categoryMap] || { color: 'from-gray-500 to-gray-700', icon: '⚙️' };
};

const getEnvironmentData = (environment: string): { color: string; icon: React.ReactElement } => {
  const environmentMap = {
    local: { color: 'from-emerald-400 to-emerald-600', icon: <ComputerDesktopIcon className="w-5 h-5" /> },
    cloud: { color: 'from-blue-400 to-blue-600', icon: <CloudIconSolid className="w-5 h-5" /> },
    hybrid: { color: 'from-purple-400 to-purple-600', icon: <ServerIcon className="w-5 h-5" /> },
  };
  return environmentMap[environment as keyof typeof environmentMap] || {
    color: 'from-gray-400 to-gray-600',
    icon: <ServerIcon className="w-5 h-5" />
  };
};

const formatRelativeTime = (date: string): string => {
  const now = new Date();
  const targetDate = new Date(date);
  const diffInSeconds = Math.floor((now.getTime() - targetDate.getTime()) / 1000);

  if (diffInSeconds < 60) return 'just now';
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
  return `${Math.floor(diffInSeconds / 86400)}d ago`;
};

export function ToolCard({
  tool,
  type,
  onEdit,
  onDelete,
  onTest,
  onClone,
  onToggleStatus,
  onManage
}: ToolCardProps) {
  const [isHovered, setIsHovered] = useState(false);
  
  const isTemplate = type === 'template';
  const template = isTemplate ? tool as ToolTemplate : null;
  const instance = !isTemplate ? tool as ToolInstance : null;
  
  const categoryData = getCategoryData(template?.category || 'utility');
  const environmentData = instance ? getEnvironmentData(instance.environment_scope) : null;

  const getStatusIcon = (status?: string) => {
    if (!status) return null;
    switch (status) {
      case 'active':
        return <CheckCircleIconSolid className="w-5 h-5 text-emerald-500" />;
      case 'inactive':
        return <PauseIcon className="w-5 h-5 text-gray-400" />;
      case 'error':
        return <ExclamationTriangleIconSolid className="w-5 h-5 text-red-500" />;
      case 'testing':
        return <BeakerIcon className="w-5 h-5 text-amber-500" />;
      default:
        return <CheckCircleIcon className="w-5 h-5 text-gray-400" />;
    }
  };

  return (
    <Card 
      className="group relative overflow-hidden transition-all duration-300 hover:shadow-2xl hover:shadow-blue-500/10 border border-gray-200/50 dark:border-gray-700/50 bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl hover:scale-[1.02]"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Gradient Background */}
      <div className={`absolute inset-0 bg-gradient-to-br ${
        isTemplate ? categoryData.color : environmentData?.color
      } opacity-0 group-hover:opacity-5 transition-opacity duration-300`} />
      
      {/* Status Indicator Strip */}
      <div className={`absolute top-0 left-0 right-0 h-1 bg-gradient-to-r ${
        isTemplate ? 'from-blue-400 to-blue-600' :
        instance?.status === 'active' ? 'from-emerald-400 to-emerald-600' :
        instance?.status === 'error' ? 'from-red-400 to-red-600' :
        instance?.status === 'testing' ? 'from-amber-400 to-amber-600' :
        'from-gray-300 to-gray-500'
      }`} />

      <CardHeader className="pb-4 relative">
        {/* Header with Icon and Actions */}
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-4">
            {/* Tool Icon with Gradient Background */}
            <div className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${
              isTemplate ? categoryData.color : environmentData?.color
            } flex items-center justify-center text-2xl shadow-lg transform group-hover:scale-110 transition-transform duration-200`}>
              {isTemplate ? categoryData.icon : environmentData?.icon}
            </div>
            
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                {!isTemplate && getStatusIcon(instance?.status)}
                <CardTitle className="text-xl font-bold text-gray-900 dark:text-white tracking-tight">
                  {tool.display_name}
                </CardTitle>
              </div>
              
              <div className="flex items-center gap-3">
                {isTemplate ? (
                  <Badge className="text-xs font-semibold px-3 py-1 rounded-full bg-blue-100 text-blue-800 border-blue-200 dark:bg-blue-900/20 dark:text-blue-300">
                    <CodeBracketIcon className="w-3 h-3 mr-1" />
                    TEMPLATE
                  </Badge>
                ) : (
                  <Badge className={`text-xs font-semibold px-3 py-1 rounded-full ${
                    instance?.status === 'active' ? 'bg-emerald-100 text-emerald-800 border-emerald-200 dark:bg-emerald-900/20 dark:text-emerald-300' :
                    instance?.status === 'error' ? 'bg-red-100 text-red-800 border-red-200 dark:bg-red-900/20 dark:text-red-300' :
                    instance?.status === 'testing' ? 'bg-amber-100 text-amber-800 border-amber-200 dark:bg-amber-900/20 dark:text-amber-300' :
                    'bg-gray-100 text-gray-800 border-gray-200 dark:bg-gray-900/20 dark:text-gray-300'
                  }`}>
                    {instance?.status?.toUpperCase() || 'INSTANCE'}
                  </Badge>
                )}
                
                {!isTemplate && instance?.environment_scope && (
                  <Badge className={`text-xs font-medium px-3 py-1 rounded-full flex items-center gap-1 ${
                    instance.environment_scope === 'cloud' ? 'bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-900/20' :
                    instance.environment_scope === 'local' ? 'bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-900/20' :
                    'bg-purple-50 text-purple-700 border-purple-200 dark:bg-purple-900/20'
                  }`}>
                    {environmentData?.icon}
                    {instance.environment_scope}
                  </Badge>
                )}

                {isTemplate && template?.category && (
                  <Badge className="text-xs font-medium px-3 py-1 rounded-full bg-gray-50 text-gray-700 border-gray-200 dark:bg-gray-800 dark:text-gray-300">
                    {template.category}
                  </Badge>
                )}
              </div>
            </div>
          </div>
          
          {/* Hover Actions */}
          <div className={`flex gap-1 transition-all duration-200 ${
            isHovered ? 'opacity-100 translate-x-0' : 'opacity-0 translate-x-4'
          }`}>
            {!isTemplate && (
              <Button
                size="icon"
                variant="ghost"
                onClick={() => onTest?.(instance!)}
                className="h-9 w-9 rounded-xl hover:bg-emerald-50 hover:text-emerald-600 dark:hover:bg-emerald-950"
              >
                <BoltIcon className="h-4 w-4" />
              </Button>
            )}
            
            <Button
              size="icon"
              variant="ghost"
              onClick={() => onEdit?.(tool)}
              className="h-9 w-9 rounded-xl hover:bg-blue-50 hover:text-blue-600 dark:hover:bg-blue-950"
            >
              <Cog6ToothIcon className="h-4 w-4" />
            </Button>
            
            <Button
              size="icon"
              variant="ghost"
              onClick={() => onClone?.(tool)}
              className="h-9 w-9 rounded-xl hover:bg-purple-50 hover:text-purple-600 dark:hover:bg-purple-950"
            >
              <DocumentDuplicateIcon className="h-4 w-4" />
            </Button>

            {!isTemplate && instance?.template_name?.toLowerCase().includes('rag') && (
              <Button
                size="icon"
                variant="ghost"
                onClick={() => onManage?.(instance)}
                className="h-9 w-9 rounded-xl hover:bg-orange-50 hover:text-orange-600 dark:hover:bg-orange-950"
              >
                <WrenchScrewdriverIcon className="h-4 w-4" />
              </Button>
            )}
          </div>
        </div>
        
        {/* Description */}
        <CardDescription className="text-sm text-gray-600 dark:text-gray-300 mt-3 line-clamp-2 leading-relaxed">
          {tool.description}
        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-6 relative">
        {/* Performance Metrics for Instances */}
        {!isTemplate && instance?.performance && (
          <div className="grid grid-cols-3 gap-3">
            <div className="text-center p-3 rounded-xl bg-gray-50/50 dark:bg-gray-800/50 border border-gray-100 dark:border-gray-700">
              <div className="text-lg font-bold text-gray-900 dark:text-white">
                {instance.performance.totalRequests || 0}
              </div>
              <div className="text-xs text-gray-500 mt-1">Requests</div>
            </div>
            
            <div className="text-center p-3 rounded-xl bg-gray-50/50 dark:bg-gray-800/50 border border-gray-100 dark:border-gray-700">
              <div className="text-lg font-bold text-emerald-600 dark:text-emerald-400">
                {Math.round(instance.performance.successRate || 0)}%
              </div>
              <div className="text-xs text-gray-500 mt-1">Success</div>
            </div>
            
            <div className="text-center p-3 rounded-xl bg-gray-50/50 dark:bg-gray-800/50 border border-gray-100 dark:border-gray-700">
              <div className="text-lg font-bold text-blue-600 dark:text-blue-400">
                {Math.round(instance.performance.averageResponseTime || 0)}ms
              </div>
              <div className="text-xs text-gray-500 mt-1">Avg Time</div>
            </div>
          </div>
        )}

        {/* Template Fields */}
        {isTemplate && template?.fields && template.fields.length > 0 && (
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 dark:text-gray-300">
              <CodeBracketIcon className="w-4 h-4" />
              Template Fields ({template.fields.length})
            </div>
            <div className="flex flex-wrap gap-2">
              {template.fields.slice(0, 3).map((field) => (
                <Badge 
                  key={field.id} 
                  variant="secondary" 
                  className={`text-xs font-medium px-3 py-1 rounded-full flex items-center gap-1 ${
                    field.is_required 
                      ? 'bg-red-50 text-red-700 border-red-200 dark:bg-red-900/20 dark:text-red-300' 
                      : 'bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-900/20 dark:text-blue-300'
                  } border-0`}
                >
                  {field.is_required && <span className="text-red-500">*</span>}
                  {field.field_label}
                </Badge>
              ))}
              {template.fields.length > 3 && (
                <Badge variant="outline" className="text-xs rounded-full">
                  +{template.fields.length - 3} more
                </Badge>
              )}
            </div>
          </div>
        )}

        {/* Instance Configuration */}
        {!isTemplate && instance?.configuration && (
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 dark:text-gray-300">
              <CpuChipIcon className="w-4 h-4" />
              Configuration
            </div>
            <div className="flex flex-wrap gap-2">
              {Object.keys(instance.configuration).slice(0, 3).map((key) => (
                <Badge 
                  key={key} 
                  variant="outline" 
                  className="text-xs rounded-full border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-400"
                >
                  {key}: {String(instance.configuration![key]).substring(0, 20)}
                </Badge>
              ))}
              {Object.keys(instance.configuration).length > 3 && (
                <Badge variant="outline" className="text-xs rounded-full">
                  +{Object.keys(instance.configuration).length - 3} more
                </Badge>
              )}
            </div>
          </div>
        )}

        {/* Footer Actions */}
        <div className="flex items-center justify-between pt-4 border-t border-gray-100/50 dark:border-gray-700/50">
          <div className="flex items-center gap-2 text-xs text-gray-500">
            <ClockIcon className="w-3 h-3" />
            Updated {formatRelativeTime(tool.updated_at)}
          </div>
          
          <div className="flex gap-2">
            {!isTemplate && onToggleStatus && (
              <Button
                size="sm"
                variant={instance?.status === 'active' ? 'outline' : 'default'}
                onClick={() => onToggleStatus(instance!)}
                className="h-8 px-3 text-xs rounded-lg font-medium"
              >
                {instance?.status === 'active' ? (
                  <>
                    <PauseIcon className="h-3 w-3 mr-1.5" />
                    Deactivate
                  </>
                ) : (
                  <>
                    <PlayIcon className="h-3 w-3 mr-1.5" />
                    Activate
                  </>
                )}
              </Button>
            )}
            
            <Button
              size="sm"
              variant="ghost"
              onClick={() => onDelete?.(tool)}
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