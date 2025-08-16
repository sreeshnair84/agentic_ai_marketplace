# Frontend Requirements - Agentic AI Acceleration

## Overview
This document outlines the comprehensive frontend requirements for the Agentic AI Acceleration with A2A Protocol integration and real-time monitoring capabilities.

## Architecture Summary
- **Framework**: Next.js 14+ with App Router
- **Language**: TypeScript 5.0+
- **Styling**: Tailwind CSS with shadcn/ui components
- **State Management**: Zustand + React Query (TanStack Query)
- **Real-time**: WebSockets for A2A monitoring
- **Charts**: Recharts + D3.js for complex visualizations
- **Testing**: Jest + Playwright for E2E testing

## Project Structure
```
frontend/
├── apps/
│   ├── web/                    # Main Next.js application
│   └── gateway/                # API Gateway frontend
├── packages/
│   ├── ui/                     # Shared UI components (shadcn/ui)
│   ├── shared/                 # Shared utilities and types
│   ├── config/                 # Shared configuration
│   ├── db/                     # Database schemas and types
│   └── sdk/                    # API SDK for backend services
└── services/                   # Frontend service workers
```

## Core Dependencies

### 1. Main Web Application (`apps/web/package.json`)
```json
{
  "name": "@lcnc/web",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev --port 3000",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "type-check": "tsc --noEmit"
  },
  "dependencies": {
    "next": "14.0.4",
    "react": "18.2.0",
    "react-dom": "18.2.0",
    "typescript": "5.3.3",
    
    "@lcnc/ui": "workspace:*",
    "@lcnc/shared": "workspace:*",
    "@lcnc/sdk": "workspace:*",
    "@lcnc/config": "workspace:*",
    
    "@tanstack/react-query": "5.17.0",
    "@tanstack/react-query-devtools": "5.17.0",
    "zustand": "4.4.7",
    "immer": "10.0.3",
    
    "tailwindcss": "3.3.6",
    "autoprefixer": "10.4.16",
    "postcss": "8.4.32",
    "clsx": "2.0.0",
    "tailwind-merge": "2.2.0",
    "tailwindcss-animate": "1.0.7",
    
    "lucide-react": "0.300.0",
    "react-icons": "4.12.0",
    
    "recharts": "2.8.0",
    "d3": "7.8.5",
    "@types/d3": "7.4.3",
    "mermaid": "10.6.1",
    "reactflow": "11.10.1",
    
    "framer-motion": "10.16.16",
    "react-hot-toast": "2.4.1",
    "sonner": "1.3.1",
    
    "react-hook-form": "7.48.2",
    "zod": "3.22.4",
    "@hookform/resolvers": "3.3.2",
    
    "date-fns": "3.0.6",
    "react-datepicker": "4.25.0",
    
    "socket.io-client": "4.7.4",
    "ws": "8.16.0",
    "@types/ws": "8.5.10",
    
    "react-split-pane": "0.1.92",
    "react-resizable-panels": "0.0.55",
    
    "monaco-editor": "0.45.0",
    "@monaco-editor/react": "4.6.0",
    
    "react-virtual": "2.10.4",
    "react-window": "1.8.8",
    "@types/react-window": "1.8.8"
  },
  "devDependencies": {
    "@types/node": "20.10.5",
    "@types/react": "18.2.45",
    "@types/react-dom": "18.2.18",
    "eslint": "8.56.0",
    "eslint-config-next": "14.0.4",
    "@typescript-eslint/parser": "6.15.0",
    "@typescript-eslint/eslint-plugin": "6.15.0",
    "prettier": "3.1.1",
    "prettier-plugin-tailwindcss": "0.5.9"
  }
}
```

### 2. UI Package (`packages/ui/package.json`)
```json
{
  "name": "@lcnc/ui",
  "version": "1.0.0",
  "main": "./src/index.ts",
  "types": "./src/index.ts",
  "dependencies": {
    "react": "18.2.0",
    "react-dom": "18.2.0",
    
    "@radix-ui/react-accordion": "1.1.2",
    "@radix-ui/react-alert-dialog": "1.0.5",
    "@radix-ui/react-avatar": "1.0.4",
    "@radix-ui/react-checkbox": "1.0.4",
    "@radix-ui/react-collapsible": "1.0.3",
    "@radix-ui/react-dialog": "1.0.5",
    "@radix-ui/react-dropdown-menu": "2.0.6",
    "@radix-ui/react-hover-card": "1.0.7",
    "@radix-ui/react-label": "2.0.2",
    "@radix-ui/react-menubar": "1.0.4",
    "@radix-ui/react-navigation-menu": "1.1.4",
    "@radix-ui/react-popover": "1.0.7",
    "@radix-ui/react-progress": "1.0.3",
    "@radix-ui/react-radio-group": "1.1.3",
    "@radix-ui/react-scroll-area": "1.0.5",
    "@radix-ui/react-select": "2.0.0",
    "@radix-ui/react-separator": "1.0.3",
    "@radix-ui/react-slider": "1.1.2",
    "@radix-ui/react-switch": "1.0.3",
    "@radix-ui/react-tabs": "1.0.4",
    "@radix-ui/react-toast": "1.1.5",
    "@radix-ui/react-toggle": "1.0.3",
    "@radix-ui/react-toggle-group": "1.0.4",
    "@radix-ui/react-tooltip": "1.0.7",
    
    "class-variance-authority": "0.7.0",
    "clsx": "2.0.0",
    "tailwind-merge": "2.2.0",
    "lucide-react": "0.300.0"
  },
  "devDependencies": {
    "@types/react": "18.2.45",
    "@types/react-dom": "18.2.18",
    "typescript": "5.3.3"
  }
}
```

### 3. SDK Package (`packages/sdk/package.json`)
```json
{
  "name": "@lcnc/sdk",
  "version": "1.0.0",
  "main": "./src/index.ts",
  "types": "./src/index.ts",
  "dependencies": {
    "axios": "1.6.2",
    "ky": "1.1.3",
    "zod": "3.22.4",
    "socket.io-client": "4.7.4",
    "@tanstack/react-query": "5.17.0"
  },
  "devDependencies": {
    "typescript": "5.3.3",
    "@types/node": "20.10.5"
  }
}
```

### 4. Shared Package (`packages/shared/package.json`)
```json
{
  "name": "@lcnc/shared",
  "version": "1.0.0",
  "main": "./src/index.ts",
  "types": "./src/index.ts",
  "dependencies": {
    "zod": "3.22.4",
    "date-fns": "3.0.6",
    "nanoid": "5.0.4",
    "lodash-es": "4.17.21",
    "@types/lodash-es": "4.17.12"
  },
  "devDependencies": {
    "typescript": "5.3.3"
  }
}
```

## Screen Components & Features

### 1. Dashboard Screen (`/dashboard`)
```typescript
// Dashboard features and components
interface DashboardFeatures {
  systemMetrics: {
    activeAgents: number;
    runningWorkflows: number;
    a2aMessages: number;
    systemHealth: string;
  };
  realTimeUpdates: {
    a2aMessageStream: WebSocket;
    metricsUpdates: EventSource;
  };
  quickActions: {
    createAgent: () => void;
    startWorkflow: () => void;
    openChat: () => void;
  };
  recentActivity: {
    agentActions: AgentAction[];
    workflowExecutions: WorkflowExecution[];
    a2aMessages: A2AMessage[];
  };
}

// Required components
const DashboardComponents = [
  "MetricsCards",
  "A2ANetworkStatus", 
  "RecentActivityFeed",
  "QuickActionPanel",
  "SystemHealthIndicator",
  "ActiveWorkflowsList"
];
```

### 2. Chat Interface (`/chat`)
```typescript
// Enhanced chat interface with A2A visualization
interface ChatFeatures {
  multiModalInput: {
    textInput: boolean;
    voiceInput: boolean;
    fileUpload: boolean;
    imageUpload: boolean;
  };
  a2aVisualization: {
    agentInteractionGraph: ReactFlowComponent;
    messageFlowDiagram: MermaidComponent;
    collaborationTimeline: TimelineComponent;
  };
  workflowSelection: {
    availableWorkflows: Workflow[];
    customWorkflowBuilder: WorkflowBuilderComponent;
  };
  agentScratchPad: {
    collapsible: boolean;
    agentThoughts: AgentThought[];
    reasoningSteps: ReasoningStep[];
  };
  exportOptions: {
    chatHistory: () => void;
    a2aTrace: () => void;
    mermaidDiagram: () => void;
  };
}
```

### 3. Agent Management (`/agents`)
```typescript
// A2A Enhanced Agent Management
interface AgentManagementFeatures {
  agentCRUD: {
    listAgents: () => Agent[];
    createAgent: (config: AgentConfig) => Agent;
    updateAgent: (id: string, config: AgentConfig) => Agent;
    deleteAgent: (id: string) => void;
  };
  a2aCapabilities: {
    registerAgentCard: (agent: Agent) => AgentCard;
    updateCapabilities: (id: string, capabilities: Capability[]) => void;
    testA2ACommunication: (agentId: string) => A2ATestResult;
  };
  frameworkIntegration: {
    supportedFrameworks: ["langchain", "llamaindex", "crewai", "semantic-kernel"];
    configTemplates: FrameworkTemplate[];
    customConfiguration: ConfigBuilder;
  };
  monitoring: {
    agentPerformance: PerformanceMetrics;
    a2aMessageHistory: A2AMessage[];
    collaborationPatterns: CollaborationPattern[];
  };
}
```

### 4. Workflow Designer (`/workflows`)
```typescript
// Visual workflow builder with A2A orchestration
interface WorkflowDesignerFeatures {
  visualBuilder: {
    reactFlowCanvas: ReactFlowComponent;
    dragDropNodes: AgentNode[];
    connectionTypes: ["sequential", "parallel", "conditional", "a2a"];
  };
  a2aOrchestration: {
    agentCollaboration: CollaborationNode;
    messageRouting: MessageRoutingNode;
    conditionalLogic: ConditionalNode;
  };
  templates: {
    predefinedWorkflows: WorkflowTemplate[];
    communityTemplates: CommunityTemplate[];
    customTemplates: CustomTemplate[];
  };
  versionControl: {
    saveVersions: () => void;
    compareVersions: (v1: string, v2: string) => Diff;
    rollbackVersion: (version: string) => void;
  };
}
```

### 5. Tools Management (`/tools`)
```typescript
// MCP and A2A tool integration
interface ToolsManagementFeatures {
  mcpIntegration: {
    serverConnections: MCPServer[];
    toolCatalog: MCPTool[];
    testToolExecution: (toolId: string) => ToolResult;
  };
  a2aToolAccess: {
    exposeToA2A: (toolId: string) => void;
    toolCapabilities: ToolCapability[];
    accessControlList: ACLEntry[];
  };
  customTools: {
    createCustomTool: (definition: ToolDefinition) => Tool;
    testingEnvironment: ToolTestEnvironment;
    dockerizedExecution: DockerToolRunner;
  };
  toolMonitoring: {
    usageStatistics: ToolUsageStats;
    performanceMetrics: ToolPerformanceMetrics;
    errorLogs: ToolErrorLog[];
  };
}
```

### 6. RAG Management (`/rag`)
```typescript
// Vector database and document management
interface RAGManagementFeatures {
  documentManagement: {
    uploadInterface: FileUploadComponent;
    supportedFormats: ["pdf", "docx", "pptx", "xlsx", "txt", "md"];
    bulkUpload: BulkUploadComponent;
    documentViewer: DocumentViewerComponent;
  };
  vectorOperations: {
    chromaCollections: ChromaCollection[];
    embeddingModels: EmbeddingModel[];
    indexConfiguration: IndexConfig;
  };
  searchInterface: {
    semanticSearch: SemanticSearchComponent;
    similaritySearch: SimilaritySearchComponent;
    qaInterface: QAComponent;
  };
  a2aIntegration: {
    exposeToAgents: boolean;
    ragCapabilities: RAGCapability[];
    queryInterface: A2AQueryInterface;
  };
}
```

### 7. Observability Dashboard (`/observability`)
```typescript
// A2A Protocol monitoring and system observability
interface ObservabilityFeatures {
  a2aMonitoring: {
    networkTopology: NetworkTopologyGraph;
    messageFlowTracing: MessageFlowComponent;
    agentInteractionHeatmap: HeatmapComponent;
  };
  distributedTracing: {
    jaegerIntegration: JaegerComponent;
    traceVisualization: TraceVisualizerComponent;
    spanAnalysis: SpanAnalysisComponent;
  };
  metricsVisualization: {
    prometheusCharts: PrometheusChartComponent;
    customDashboards: CustomDashboardBuilder;
    alertingRules: AlertingRuleManager;
  };
  realTimeMonitoring: {
    liveMetrics: LiveMetricsComponent;
    eventStream: EventStreamComponent;
    systemHealth: SystemHealthComponent;
  };
}
```

## State Management Architecture

### 1. Zustand Store Structure
```typescript
// Global state management with Zustand
interface AppState {
  // Authentication
  auth: {
    user: User | null;
    token: string | null;
    isAuthenticated: boolean;
  };
  
  // A2A Protocol State
  a2a: {
    registeredAgents: AgentCard[];
    activeConnections: A2AConnection[];
    messageQueue: A2AMessage[];
    networkTopology: NetworkNode[];
  };
  
  // UI State
  ui: {
    theme: "light" | "dark";
    sidebarCollapsed: boolean;
    activeWorkspace: string;
    notifications: Notification[];
  };
  
  // Real-time Data
  realTime: {
    systemMetrics: SystemMetrics;
    agentStatuses: AgentStatus[];
    workflowExecutions: WorkflowExecution[];
  };
}

// Store actions
interface AppActions {
  // Auth actions
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<void>;
  
  // A2A actions
  registerAgent: (agentCard: AgentCard) => void;
  sendA2AMessage: (message: A2AMessage) => Promise<A2AResponse>;
  updateNetworkTopology: (topology: NetworkNode[]) => void;
  
  // UI actions
  toggleTheme: () => void;
  toggleSidebar: () => void;
  addNotification: (notification: Notification) => void;
  removeNotification: (id: string) => void;
}
```

### 2. React Query Configuration
```typescript
// API state management with React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      cacheTime: 1000 * 60 * 30, // 30 minutes
      retry: (failureCount, error) => {
        if (error.status === 404) return false;
        return failureCount < 3;
      },
    },
    mutations: {
      retry: 1,
    },
  },
});

// Query keys factory
export const queryKeys = {
  agents: {
    all: ['agents'] as const,
    list: (filters: AgentFilters) => [...queryKeys.agents.all, 'list', filters] as const,
    detail: (id: string) => [...queryKeys.agents.all, 'detail', id] as const,
    capabilities: (id: string) => [...queryKeys.agents.all, 'capabilities', id] as const,
  },
  workflows: {
    all: ['workflows'] as const,
    list: (filters: WorkflowFilters) => [...queryKeys.workflows.all, 'list', filters] as const,
    detail: (id: string) => [...queryKeys.workflows.all, 'detail', id] as const,
    executions: (id: string) => [...queryKeys.workflows.all, 'executions', id] as const,
  },
  a2a: {
    all: ['a2a'] as const,
    network: () => [...queryKeys.a2a.all, 'network'] as const,
    messages: (agentId: string) => [...queryKeys.a2a.all, 'messages', agentId] as const,
    trace: (traceId: string) => [...queryKeys.a2a.all, 'trace', traceId] as const,
  },
};
```

## Real-time Communication

### 1. WebSocket Integration
```typescript
// WebSocket hooks for real-time updates
export function useA2AMessageStream() {
  const [messages, setMessages] = useState<A2AMessage[]>([]);
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected'>('disconnected');
  
  useEffect(() => {
    const ws = new WebSocket(`${process.env.NEXT_PUBLIC_WS_URL}/a2a/stream`);
    
    ws.onopen = () => setConnectionStatus('connected');
    ws.onclose = () => setConnectionStatus('disconnected');
    ws.onmessage = (event) => {
      const message = JSON.parse(event.data) as A2AMessage;
      setMessages(prev => [...prev, message]);
    };
    
    return () => ws.close();
  }, []);
  
  return { messages, connectionStatus };
}

// Socket.IO integration for observability
export function useObservabilitySocket() {
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null);
  
  useEffect(() => {
    const socket = io(`${process.env.NEXT_PUBLIC_API_URL}/observability`);
    
    socket.on('metrics', (data: SystemMetrics) => {
      setMetrics(data);
    });
    
    socket.on('a2a_event', (event: A2AEvent) => {
      // Handle A2A events
    });
    
    return () => socket.disconnect();
  }, []);
  
  return { metrics };
}
```

### 2. Server-Sent Events
```typescript
// SSE for real-time notifications
export function useNotificationStream() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  
  useEffect(() => {
    const eventSource = new EventSource(`${process.env.NEXT_PUBLIC_API_URL}/events/stream`);
    
    eventSource.onmessage = (event) => {
      const notification = JSON.parse(event.data) as Notification;
      setNotifications(prev => [...prev, notification]);
    };
    
    return () => eventSource.close();
  }, []);
  
  return { notifications };
}
```

## Testing Strategy

### 1. Unit Testing (Jest)
```typescript
// Component testing with Jest and Testing Library
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AgentManagement } from '../AgentManagement';

describe('AgentManagement', () => {
  let queryClient: QueryClient;
  
  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    });
  });
  
  it('should display list of agents', async () => {
    // Mock API response
    const mockAgents = [
      { id: '1', name: 'Agent 1', capabilities: ['chat'] },
      { id: '2', name: 'Agent 2', capabilities: ['search'] },
    ];
    
    render(
      <QueryClientProvider client={queryClient}>
        <AgentManagement />
      </QueryClientProvider>
    );
    
    await waitFor(() => {
      expect(screen.getByText('Agent 1')).toBeInTheDocument();
      expect(screen.getByText('Agent 2')).toBeInTheDocument();
    });
  });
  
  it('should handle A2A message sending', async () => {
    // Test A2A functionality
  });
});
```

### 2. E2E Testing (Playwright)
```typescript
// E2E tests for critical workflows
import { test, expect } from '@playwright/test';

test.describe('A2A Agent Collaboration', () => {
  test('should create and test agent collaboration workflow', async ({ page }) => {
    await page.goto('/workflows');
    
    // Create new workflow
    await page.click('[data-testid="create-workflow"]');
    await page.fill('[data-testid="workflow-name"]', 'A2A Test Workflow');
    
    // Add agents to workflow
    await page.drag('[data-testid="agent-node"]', '[data-testid="canvas"]');
    await page.drag('[data-testid="a2a-connection"]', '[data-testid="canvas"]');
    
    // Configure A2A communication
    await page.click('[data-testid="configure-a2a"]');
    await page.selectOption('[data-testid="message-type"]', 'collaboration');
    
    // Save and execute workflow
    await page.click('[data-testid="save-workflow"]');
    await page.click('[data-testid="execute-workflow"]');
    
    // Verify execution
    await expect(page.locator('[data-testid="execution-status"]')).toContainText('Running');
    await expect(page.locator('[data-testid="a2a-messages"]')).toBeVisible();
  });
});
```

## Performance Optimization

### 1. Code Splitting
```typescript
// Lazy loading for large components
import { lazy, Suspense } from 'react';

const WorkflowDesigner = lazy(() => import('./WorkflowDesigner'));
const ObservabilityDashboard = lazy(() => import('./ObservabilityDashboard'));

// Route-based code splitting
export function App() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <Routes>
        <Route path="/workflows" element={<WorkflowDesigner />} />
        <Route path="/observability" element={<ObservabilityDashboard />} />
      </Routes>
    </Suspense>
  );
}
```

### 2. Virtual Scrolling
```typescript
// Virtual scrolling for large lists
import { FixedSizeList as List } from 'react-window';

export function AgentList({ agents }: { agents: Agent[] }) {
  const Row = ({ index, style }: { index: number; style: React.CSSProperties }) => (
    <div style={style}>
      <AgentCard agent={agents[index]} />
    </div>
  );
  
  return (
    <List
      height={600}
      itemCount={agents.length}
      itemSize={120}
      width="100%"
    >
      {Row}
    </List>
  );
}
```

## Environment Configuration

### Development (.env.local)
```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
NEXT_PUBLIC_GATEWAY_URL=http://localhost:8000

# A2A Protocol
NEXT_PUBLIC_A2A_ENABLED=true
NEXT_PUBLIC_A2A_DEBUG=true

# Feature Flags
NEXT_PUBLIC_ENABLE_CHAT=true
NEXT_PUBLIC_ENABLE_WORKFLOWS=true
NEXT_PUBLIC_ENABLE_OBSERVABILITY=true

# Analytics
NEXT_PUBLIC_ANALYTICS_ID=
NEXT_PUBLIC_MONITORING_URL=

# Development
NEXT_PUBLIC_DEBUG=true
NEXT_PUBLIC_LOG_LEVEL=debug
```

### Production (.env.production)
```bash
# API Configuration
NEXT_PUBLIC_API_URL=https://api.lcnc-platform.com
NEXT_PUBLIC_WS_URL=wss://api.lcnc-platform.com
NEXT_PUBLIC_GATEWAY_URL=https://api.lcnc-platform.com

# A2A Protocol
NEXT_PUBLIC_A2A_ENABLED=true
NEXT_PUBLIC_A2A_DEBUG=false

# Security
NEXT_PUBLIC_CSP_NONCE=
NEXT_PUBLIC_SECURITY_HEADERS=true

# Performance
NEXT_PUBLIC_CDN_URL=https://cdn.lcnc-platform.com
NEXT_PUBLIC_CACHE_STRATEGY=aggressive

# Analytics
NEXT_PUBLIC_ANALYTICS_ID=GA_MEASUREMENT_ID
NEXT_PUBLIC_MONITORING_URL=https://monitoring.lcnc-platform.com
```

## Build Configuration

### Next.js Config (`next.config.mjs`)
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    typedRoutes: true,
    serverActions: true,
  },
  
  // Enable SWC minification
  swcMinify: true,
  
  // Webpack configuration for Monaco Editor
  webpack: (config) => {
    config.module.rules.push({
      test: /\.worker\.js$/,
      use: { loader: 'worker-loader' },
    });
    return config;
  },
  
  // Environment variables
  env: {
    CUSTOM_KEY: process.env.CUSTOM_KEY,
  },
  
  // Headers for security
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'origin-when-cross-origin',
          },
        ],
      },
    ];
  },
  
  // Redirects
  async redirects() {
    return [
      {
        source: '/',
        destination: '/dashboard',
        permanent: false,
      },
    ];
  },
  
  // Image optimization
  images: {
    domains: ['localhost', 'api.lcnc-platform.com'],
    formats: ['image/webp', 'image/avif'],
  },
};

export default nextConfig;
```

### Tailwind Config (`tailwind.config.js`)
```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
    './src/**/*.{ts,tsx}',
    '../packages/ui/src/**/*.{ts,tsx}',
  ],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        // A2A Protocol specific colors
        a2a: {
          message: "hsl(var(--a2a-message))",
          agent: "hsl(var(--a2a-agent))",
          connection: "hsl(var(--a2a-connection))",
        },
        // Service specific colors
        agent: {
          DEFAULT: "hsl(var(--agent))",
          foreground: "hsl(var(--agent-foreground))",
        },
        workflow: {
          DEFAULT: "hsl(var(--workflow))",
          foreground: "hsl(var(--workflow-foreground))",
        },
        tool: {
          DEFAULT: "hsl(var(--tool))",
          foreground: "hsl(var(--tool-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      keyframes: {
        "accordion-down": {
          from: { height: 0 },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: 0 },
        },
        // A2A specific animations
        "a2a-pulse": {
          "0%, 100%": { opacity: 1 },
          "50%": { opacity: 0.5 },
        },
        "agent-connect": {
          "0%": { transform: "scale(1)", opacity: 0.7 },
          "50%": { transform: "scale(1.1)", opacity: 1 },
          "100%": { transform: "scale(1)", opacity: 0.7 },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
        "a2a-pulse": "a2a-pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "agent-connect": "agent-connect 3s ease-in-out infinite",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}
```

This comprehensive frontend requirements document ensures the Next.js application is properly configured for A2A protocol integration, real-time monitoring, and enterprise-grade user experience.
