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
  ChartBarIcon
} from '@heroicons/react/24/outline';

interface Agent {
  id: string;
  name: string;
  description: string;
  framework: 'langchain' | 'llamaindex' | 'crewai' | 'semantic-kernel';
  skills: string[];
  status: 'active' | 'inactive' | 'error' | 'draft';
  version: string;
  createdAt: Date;
  updatedAt: Date;
  lastExecutedAt?: Date;
  executionCount: number;
  systemPrompt?: string;
  tags: string[];
  config: any;
}

interface AgentCardProps {
  agent: Agent;
  onEdit?: (agent: Agent) => void;
  onDelete?: (agent: Agent) => void;
  onToggleStatus?: (agent: Agent) => void;
  onExecute?: (agent: Agent) => void;
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

const getFrameworkIcon = (framework: string): string => {
  const icons = {
    langchain: '🦜',
    llamaindex: '🦙',
    crewai: '👥',
    'semantic-kernel': '🧠',
  };
  return icons[framework as keyof typeof icons] || '🤖';
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
  onExecute 
}: AgentCardProps) {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <Card 
      className="relative transition-all duration-200 hover:shadow-lg border-2 hover:border-blue-200"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="text-2xl">
              {getFrameworkIcon(agent.framework)}
            </div>
            <div>
              <CardTitle className="text-lg font-semibold text-gray-900 dark:text-white">
                {agent.name}
              </CardTitle>
              <div className="flex items-center gap-2 mt-1">
                <Badge
                  className={`text-xs font-medium border ${getStatusColor(agent.status)}`}
                >
                  {agent.status}
                </Badge>
                <span className="text-xs text-gray-500">v{agent.version}</span>
              </div>
            </div>
          </div>
          
          {/* Action buttons - show on hover */}
          <div className={`flex gap-1 transition-opacity duration-200 ${
            isHovered ? 'opacity-100' : 'opacity-0'
          }`}>
            {onExecute && (
              <Button
                size="icon"
                variant="ghost"
                onClick={() => onExecute(agent)}
                className="h-8 w-8"
              >
                <PlayIcon className="h-4 w-4" />
              </Button>
            )}
            {onEdit && (
              <Button
                size="icon"
                variant="ghost"
                onClick={() => onEdit(agent)}
                className="h-8 w-8"
              >
                <PencilIcon className="h-4 w-4" />
              </Button>
            )}
          </div>
        </div>
        
        <CardDescription className="text-sm text-gray-600 dark:text-gray-400 mt-2">
          {agent.description}
        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Framework and Skills */}
        <div>
          <div className="text-xs font-medium text-gray-500 mb-2">Framework & Skills</div>
          <div className="flex flex-wrap gap-1">
            <Badge variant="outline" className="text-xs">
              {agent.framework}
            </Badge>
            {agent.skills.slice(0, 3).map((skill) => (
              <Badge key={skill} variant="secondary" className="text-xs">
                {skill}
              </Badge>
            ))}
            {agent.skills.length > 3 && (
              <Badge variant="outline" className="text-xs">
                +{agent.skills.length - 3} more
              </Badge>
            )}
          </div>
        </div>

        {/* Metrics */}
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div className="flex items-center gap-2">
            <ChartBarIcon className="h-4 w-4 text-gray-400" />
            <div>
              <div className="font-medium text-gray-900 dark:text-white">
                {agent.executionCount}
              </div>
              <div className="text-xs text-gray-500">executions</div>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <ClockIcon className="h-4 w-4 text-gray-400" />
            <div>
              <div className="font-medium text-gray-900 dark:text-white">
                {agent.lastExecutedAt 
                  ? formatRelativeTime(agent.lastExecutedAt)
                  : 'Never'
                }
              </div>
              <div className="text-xs text-gray-500">last run</div>
            </div>
          </div>
        </div>

        {/* Tags */}
        {agent.tags.length > 0 && (
          <div>
            <div className="text-xs font-medium text-gray-500 mb-2">Tags</div>
            <div className="flex flex-wrap gap-1">
              {agent.tags.map((tag) => (
                <Badge key={tag} variant="outline" className="text-xs">
                  #{tag}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* Footer Actions */}
        <div className="flex items-center justify-between pt-2 border-t border-gray-100 dark:border-gray-800">
          <div className="text-xs text-gray-500">
            Updated {formatRelativeTime(agent.updatedAt)}
          </div>
          
          <div className="flex gap-2">
            {onToggleStatus && (
              <Button
                size="sm"
                variant="outline"
                onClick={() => onToggleStatus(agent)}
                className="h-7 px-2 text-xs"
              >
                {agent.status === 'active' ? (
                  <>
                    <PauseIcon className="h-3 w-3 mr-1" />
                    Pause
                  </>
                ) : (
                  <>
                    <PlayIcon className="h-3 w-3 mr-1" />
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
                className="h-7 px-2 text-xs"
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
