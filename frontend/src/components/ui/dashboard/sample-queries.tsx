'use client';

import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import Search from '@/components/ui/search';
import { PlayIcon, BookOpenIcon, WrenchScrewdriverIcon, CpuChipIcon } from '@heroicons/react/24/outline';

interface SampleQuery {
  id: string;
  category: string;
  query: string;
  description: string;
  complexity_level: string;
  tags: string[];
  is_featured: boolean;
}

interface SampleQueriesData {
  agents: SampleQuery[];
  tools: SampleQuery[];
  workflows: SampleQuery[];
}

const complexityColors = {
  beginner: 'bg-green-100 text-green-800 border-green-200',
  intermediate: 'bg-yellow-100 text-yellow-800 border-yellow-200',
  advanced: 'bg-red-100 text-red-800 border-red-200'
};

const serviceIcons = {
  agents: CpuChipIcon,
  tools: WrenchScrewdriverIcon,
  workflows: BookOpenIcon
};

export default function SampleQueries() {
  const [queries, setQueries] = useState<SampleQueriesData>({ agents: [], tools: [], workflows: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [activeTab, setActiveTab] = useState('featured');

  useEffect(() => {
    fetchSampleQueries();
  }, []);

  const fetchSampleQueries = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/v1/sample-queries/');
      
      if (!response.ok) {
        throw new Error('Failed to fetch sample queries');
      }
      
      const data = await response.json();
      setQueries(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleExecuteQuery = async (query: SampleQuery, serviceType: string) => {
    // This is where you would integrate with your execution system
    console.log(`Executing ${serviceType} query:`, query.query);
    
    // For demo purposes, show a notification
    alert(`Demo: Would execute "${query.query}" for ${serviceType}`);
  };

  const filteredQueries = (queryList: SampleQuery[]) => {
    if (!searchTerm) return queryList;
    return queryList.filter(q => 
      q.query.toLowerCase().includes(searchTerm.toLowerCase()) ||
      q.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
      q.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()))
    );
  };

  const featuredQueries = [
    ...queries.agents.filter(q => q.is_featured),
    ...queries.tools.filter(q => q.is_featured),
    ...queries.workflows.filter(q => q.is_featured)
  ];

  const renderQueryCard = (query: SampleQuery, serviceType: string) => {
    const IconComponent = serviceIcons[serviceType as keyof typeof serviceIcons];
    
    return (
      <Card key={query.id} className="p-4 hover:shadow-md transition-shadow">
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-2">
            <IconComponent className="h-5 w-5 text-blue-600" />
            <Badge variant="outline" className="text-xs">
              {serviceType} / {query.category}
            </Badge>
          </div>
          <Badge 
            variant="outline" 
            className={`text-xs ${complexityColors[query.complexity_level as keyof typeof complexityColors]}`}
          >
            {query.complexity_level}
          </Badge>
        </div>
        
        <h3 className="font-medium text-gray-900 mb-2 leading-tight">
          {query.query}
        </h3>
        
        <p className="text-sm text-gray-600 mb-3">
          {query.description}
        </p>
        
        <div className="flex flex-wrap gap-1 mb-3">
          {query.tags.map((tag) => (
            <Badge key={tag} variant="secondary" className="text-xs">
              {tag}
            </Badge>
          ))}
        </div>
        
        <Button 
          size="sm" 
          onClick={() => handleExecuteQuery(query, serviceType)}
          className="w-full"
        >
          <PlayIcon className="h-4 w-4 mr-2" />
          Try This Query
        </Button>
      </Card>
    );
  };

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold">Sample Queries</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <Card key={i} className="p-4">
              <div className="animate-pulse">
                <div className="h-4 bg-gray-200 rounded mb-2"></div>
                <div className="h-3 bg-gray-200 rounded mb-3"></div>
                <div className="h-8 bg-gray-200 rounded"></div>
              </div>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <Card className="p-6">
        <div className="text-center">
          <h3 className="text-lg font-medium text-red-800 mb-2">Error Loading Sample Queries</h3>
          <p className="text-red-600 mb-4">{error}</p>
          <Button onClick={fetchSampleQueries} variant="outline">
            Try Again
          </Button>
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Sample Queries</h2>
        <div className="w-72">
          <Search 
            placeholder="Search queries..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="featured">⭐ Featured</TabsTrigger>
          <TabsTrigger value="agents">🤖 Agents</TabsTrigger>
          <TabsTrigger value="tools">🔧 Tools</TabsTrigger>
          <TabsTrigger value="workflows">📋 Workflows</TabsTrigger>
        </TabsList>

        <TabsContent value="featured" className="mt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredQueries(featuredQueries).map((query) => {
              // Determine service type from the original data
              const serviceType = queries.agents.includes(query) ? 'agents' :
                                queries.tools.includes(query) ? 'tools' : 'workflows';
              return renderQueryCard(query, serviceType);
            })}
          </div>
          {filteredQueries(featuredQueries).length === 0 && (
            <Card className="p-8 text-center text-gray-500">
              {searchTerm ? 'No featured queries match your search.' : 'No featured queries available.'}
            </Card>
          )}
        </TabsContent>

        <TabsContent value="agents" className="mt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredQueries(queries.agents).map((query) => renderQueryCard(query, 'agents'))}
          </div>
          {filteredQueries(queries.agents).length === 0 && (
            <Card className="p-8 text-center text-gray-500">
              {searchTerm ? 'No agent queries match your search.' : 'No agent queries available.'}
            </Card>
          )}
        </TabsContent>

        <TabsContent value="tools" className="mt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredQueries(queries.tools).map((query) => renderQueryCard(query, 'tools'))}
          </div>
          {filteredQueries(queries.tools).length === 0 && (
            <Card className="p-8 text-center text-gray-500">
              {searchTerm ? 'No tool queries match your search.' : 'No tool queries available.'}
            </Card>
          )}
        </TabsContent>

        <TabsContent value="workflows" className="mt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredQueries(queries.workflows).map((query) => renderQueryCard(query, 'workflows'))}
          </div>
          {filteredQueries(queries.workflows).length === 0 && (
            <Card className="p-8 text-center text-gray-500">
              {searchTerm ? 'No workflow queries match your search.' : 'No workflow queries available.'}
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
