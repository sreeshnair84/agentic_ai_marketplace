'use client';

import { ChevronDownIcon } from '@heroicons/react/24/outline';

interface AgentFiltersProps {
  selectedFramework: string;
  selectedStatus: string;
  onFrameworkChange: (framework: string) => void;
  onStatusChange: (status: string) => void;
}

export function AgentFilters({
  selectedFramework,
  selectedStatus,
  onFrameworkChange,
  onStatusChange,
}: AgentFiltersProps) {
  const frameworks = [
    { value: 'all', label: 'All Frameworks' },
    { value: 'langchain', label: 'LangChain 🦜' },
    { value: 'llamaindex', label: 'LlamaIndex 🦙' },
    { value: 'crewai', label: 'CrewAI 👥' },
    { value: 'semantic-kernel', label: 'Semantic Kernel 🧠' },
  ];

  const statuses = [
    { value: 'all', label: 'All Status' },
    { value: 'active', label: 'Active' },
    { value: 'inactive', label: 'Inactive' },
    { value: 'error', label: 'Error' },
    { value: 'draft', label: 'Draft' },
  ];

  return (
    <div className="flex gap-4">
      <div className="relative">
        <select
          value={selectedFramework}
          onChange={(e) => onFrameworkChange(e.target.value)}
          className="appearance-none bg-white dark:bg-gray-950 border border-gray-300 dark:border-gray-800 rounded-md px-4 py-2 pr-8 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          {frameworks.map((framework) => (
            <option key={framework.value} value={framework.value}>
              {framework.label}
            </option>
          ))}
        </select>
        <ChevronDownIcon className="absolute right-2 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400 pointer-events-none" />
      </div>

      <div className="relative">
        <select
          value={selectedStatus}
          onChange={(e) => onStatusChange(e.target.value)}
          className="appearance-none bg-white dark:bg-gray-950 border border-gray-300 dark:border-gray-800 rounded-md px-4 py-2 pr-8 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          {statuses.map((status) => (
            <option key={status.value} value={status.value}>
              {status.label}
            </option>
          ))}
        </select>
        <ChevronDownIcon className="absolute right-2 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400 pointer-events-none" />
      </div>
    </div>
  );
}
