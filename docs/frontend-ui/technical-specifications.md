# Frontend UI - Technical Specifications & Design System

## Overview

The Enterprise AI Platform frontend is built with Next.js 15.4.0, TypeScript, and modern React patterns. This document establishes the **mandatory design system and layout standards** that all modules must follow to ensure consistency, maintainability, and excellent user experience.

## Design System Principles

### 1. Consistency First
- All pages must use the same layout pattern
- Components must follow established naming conventions
- UI spacing, typography, and colors must be standardized

### 2. Accessibility & Performance
- WCAG 2.1 AA compliance is mandatory
- Components must be keyboard navigable
- Performance optimizations are built-in to the design system

### 3. Responsive Design
- Mobile-first approach
- Consistent breakpoints across all components
- Flexible layouts that work on all screen sizes

### 4. Maintainability
- Centralized component library
- Standardized props and patterns
- Clear separation of concerns

## MANDATORY Layout Standards

### 1. Page Structure Requirements

All pages MUST follow this exact structure:

```tsx
'use client';

import { AuthGuard } from '@/components/auth/AuthGuard';
import { StandardPageLayout, StandardSection, StandardGrid, StandardCard } from '@/components/layout/StandardPageLayout';
// Other imports...

export default function PageName() {
  return (
    <AuthGuard>
      <StandardPageLayout
        title="Page Title"
        description="Page description"
        actions={<div><!-- Action buttons --></div>}
      >
        <StandardSection>
          <!-- Page content sections -->
        </StandardSection>
      </StandardPageLayout>
    </AuthGuard>
  );
}
```

### 2. Layout Component Standards

#### StandardPageLayout
**REQUIRED PROPS:**
- `title`: string - The main page title
- `description`: string - Page description/subtitle
- `actions`: ReactNode - Action buttons (optional)

**OPTIONAL PROPS:**
- `variant`: 'default' | 'narrow' | 'wide' | 'full'
- `breadcrumbs`: Array<{ label: string; href?: string }>

#### StandardSection
Used for grouping related content within a page.

**PROPS:**
- `title`: string (optional) - Section title
- `description`: string (optional) - Section description
- `actions`: ReactNode (optional) - Section-specific actions
- `variant`: 'default' | 'card' | 'bordered'

#### StandardGrid
Responsive grid system for consistent layouts.

**PROPS:**
- `cols`: Object - Responsive column configuration
  ```tsx
  cols={{ default: 1, sm: 2, md: 3, lg: 4 }}
  ```
- `gap`: 'sm' | 'md' | 'lg' | 'xl'

#### StandardCard
Consistent card component for content containers.

**PROPS:**
- `title`: string (optional) - Card title
- `description`: string (optional) - Card description
- `actions`: ReactNode (optional) - Card actions
- `variant`: 'default' | 'elevated' | 'outlined' | 'ghost'
- `padding`: 'sm' | 'md' | 'lg'

### 3. Typography Standards

**MANDATORY CLASSES:**
- Page titles: `text-display-2`
- Section titles: `text-heading-1`
- Card titles: `text-heading-2`
- Subsection titles: `text-heading-3`
- Body text: `text-body`
- Small text: `text-body-sm`
- Captions: `text-caption`

### 4. Color & Spacing Standards

**STATUS COLORS:**
- Success: `text-green-600`, `bg-green-50`, `border-green-200`
- Warning: `text-yellow-600`, `bg-yellow-50`, `border-yellow-200`
- Error: `text-red-600`, `bg-red-50`, `border-red-200`
- Info: `text-blue-600`, `bg-blue-50`, `border-blue-200`

**SPACING:**
- Section spacing: `space-y-6`
- Card padding: `p-6`
- Grid gaps: `gap-6`
- Button spacing: `space-x-3`

### 5. Component Patterns

#### Search & Filters Pattern
```tsx
<StandardSection>
  <div className="flex flex-col sm:flex-row gap-4">
    <div className="relative flex-1">
      <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
      <Input
        placeholder="Search..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        className="pl-10"
      />
    </div>
    <!-- Filter components -->
  </div>
</StandardSection>
```

#### Stats Cards Pattern
```tsx
<StandardSection>
  <StandardGrid cols={{ default: 1, sm: 2, lg: 4 }} gap="md">
    <StandardCard>
      <div className="pb-2">
        <div className="text-3xl font-bold text-blue-600">
          {statValue}
        </div>
        <p className="text-body-sm text-gray-600 dark:text-gray-400">
          Stat Label
        </p>
      </div>
    </StandardCard>
  </StandardGrid>
</StandardSection>
```

#### Data Grid Pattern
```tsx
<StandardSection>
  <StandardGrid cols={{ default: 1, md: 2, lg: 3 }} gap="md">
    {items.map((item) => (
      <StandardCard key={item.id}>
        <!-- Card content -->
      </StandardCard>
    ))}
  </StandardGrid>
</StandardSection>
```

## Technology Stack

### Core Framework
| Technology | Version | Purpose | Health Check |
|------------|---------|---------|--------------|
| Next.js | 15.4.0 | React framework with App Router | `http://localhost:3000/api/health` |
| React | 19.1.0 | UI library with concurrent features | Built into Next.js |
| TypeScript | 5.7.3 | Type safety and developer experience | Compile-time |
| Tailwind CSS | 3.4.17 | Utility-first CSS framework | Build-time |

### UI Component Library
```json
{
  "ui-components": {
    "@radix-ui/react-accordion": "^1.1.2",
    "@radix-ui/react-alert-dialog": "^1.0.5",
    "@radix-ui/react-avatar": "^1.0.4",
    "@radix-ui/react-checkbox": "^1.0.4",
    "@radix-ui/react-dialog": "^1.0.5",
    "@radix-ui/react-dropdown-menu": "^2.0.6",
    "@radix-ui/react-hover-card": "^1.0.7",
    "@radix-ui/react-label": "^2.0.2",
    "@radix-ui/react-popover": "^1.0.7",
    "@radix-ui/react-select": "^2.0.0",
    "@radix-ui/react-separator": "^1.0.3",
    "@radix-ui/react-slider": "^1.1.2",
    "@radix-ui/react-switch": "^1.0.3",
    "@radix-ui/react-tabs": "^1.0.4",
    "@radix-ui/react-toast": "^1.1.5",
    "@radix-ui/react-tooltip": "^1.0.7"
  }
}
```

### State Management & Data Fetching
```json
{
  "state-management": {
    "zustand": "^4.5.0",
    "@tanstack/react-query": "^5.28.0",
    "@tanstack/react-query-devtools": "^5.28.0",
    "axios": "^1.6.0"
  }
}
```

### Visualization & Interactive Components
```json
{
  "visualization": {
    "recharts": "^2.12.0",
    "d3": "^7.9.0",
    "reactflow": "^11.11.0",
    "@xyflow/react": "^12.0.0",
    "cytoscape": "^3.28.0",
    "mermaid": "^10.9.0"
  }
}
```

## Project Structure

```
frontend/
├── public/                          # Static assets
│   ├── customers/                   # Customer avatars
│   ├── favicon.ico
│   ├── hero-desktop.png
│   ├── hero-mobile.png
│   └── opengraph-image.png
├── src/
│   ├── app/                        # Next.js App Router
│   │   ├── globals.css            # Global styles
│   │   ├── layout.tsx             # Root layout
│   │   ├── page.tsx               # Home page
│   │   ├── (auth)/                # Auth group
│   │   │   ├── login/page.tsx
│   │   │   ├── register/page.tsx
│   │   │   └── callback/[provider]/page.tsx
│   │   ├── login/page.tsx         # Login page
│   │   ├── dashboard/page.tsx     # Dashboard page
│   │   ├── agents/                # Agent management
│   │   │   ├── page.tsx
│   │   │   └── components/
│   │   │       ├── AgentCard.tsx
│   │   │       ├── AgentFilters.tsx
│   │   │       └── CreateAgentDialog.tsx
│   │   ├── chat/page.tsx          # A2A Chat interface
│   │   ├── workflows/page.tsx     # Workflow management
│   │   ├── tools/                 # Tool management
│   │   │   ├── page.tsx
│   │   │   ├── llm-models/page.tsx
│   │   │   └── components/
│   │   │       ├── AgentTemplateBuilder.tsx
│   │   │       ├── LLMModelForm.tsx
│   │   │       ├── PhysicalToolTester.tsx
│   │   │       ├── RAGPipelineBuilder.tsx
│   │   │       ├── ToolInstanceForm.tsx
│   │   │       └── ToolTemplateForm.tsx
│   │   ├── models/                # Model management
│   │   │   ├── layout.tsx
│   │   │   ├── llm-models/page.tsx
│   │   │   ├── embedding-models/page.tsx
│   │   │   └── components/
│   │   │       ├── EmbeddingModelForm.tsx
│   │   │       └── LLMModelForm.tsx
│   │   ├── mcp/                   # MCP management
│   │   │   ├── page.tsx
│   │   │   └── components/
│   │   │       ├── MCPEndpointForm.tsx
│   │   │       ├── MCPServerForm.tsx
│   │   │       └── MCPToolTester.tsx
│   │   ├── rag/page.tsx           # RAG management
│   │   ├── observability/page.tsx # Monitoring
│   │   ├── environment/page.tsx   # Environment settings
│   │   ├── projects/page.tsx      # Project management
│   │   ├── settings/page.tsx      # Settings
│   │   ├── templates/tools/page.tsx # Tool templates
│   │   └── api/                   # API routes
│   │       ├── agents/route.ts
│   │       ├── dashboard/route.ts
│   │       ├── query/route.ts
│   │       ├── seed/route.ts
│   │       ├── sidebar/
│   │       │   ├── route.ts
│   │       │   └── stats/route.ts
│   │       └── test-backend/route.ts
│   ├── components/                # React components
│   │   ├── layout/               # Layout components
│   │   │   ├── ConsistentLayout.tsx
│   │   │   ├── PageContainer.tsx
│   │   │   └── StandardPageLayout.tsx
│   │   ├── navigation/           # Navigation components
│   │   │   └── Navigation.tsx
│   │   ├── auth/                 # Authentication
│   │   │   ├── AuthGuard.tsx
│   │   │   ├── LoginForm.tsx
│   │   │   └── RegisterForm.tsx
│   │   ├── chat/                 # Chat components
│   │   │   └── A2AChatInterface.tsx
│   │   └── ui/                   # shadcn/ui components
│   │       ├── acme-logo.tsx
│   │       ├── alert.tsx
│   │       ├── badge.tsx
│   │       ├── button.tsx
│   │       ├── card.tsx
│   │       ├── dialog.tsx
│   │       ├── input.tsx
│   │       ├── label.tsx
│   │       ├── login-form.tsx
│   │       ├── progress.tsx
│   │       ├── scroll-area.tsx
│   │       ├── search.tsx
│   │       ├── select.tsx
│   │       ├── separator.tsx
│   │       ├── skeleton.tsx
│   │       ├── skeletons.tsx
│   │       ├── switch.tsx
│   │       ├── table.tsx
│   │       ├── tabs.tsx
│   │       ├── textarea.tsx
│   │       ├── tooltip.tsx
│   │       ├── customers/
│   │       │   └── table.tsx
│   │       ├── dashboard/
│   │       │   ├── cards.tsx
│   │       │   ├── latest-invoices.tsx
│   │       │   ├── nav-links.tsx
│   │       │   ├── revenue-chart.tsx
│   │       │   ├── sample-queries.tsx
│   │       │   └── sidenav.tsx
│   │       └── invoices/
│   │           ├── breadcrumbs.tsx
│   │           ├── buttons.tsx
│   │           ├── create-form.tsx
│   │           ├── edit-form.tsx
│   │           ├── pagination.tsx
│   │           ├── status.tsx
│   │           └── table.tsx
│   ├── hooks/                    # Custom React hooks
│   │   ├── use-toast.ts
│   │   ├── useA2AChat.ts
│   │   ├── useA2AChatFastAPI.ts
│   │   ├── useAgents.ts
│   │   ├── useDashboardData.ts
│   │   ├── useEmbeddingModels.ts
│   │   ├── useLLMModels.ts
│   │   ├── useMCP.ts
│   │   ├── useMCP_new.ts
│   │   ├── useRAG.ts
│   │   ├── useSidebarStats.ts
│   │   ├── useTools.ts
│   │   └── useWorkflows.ts
│   ├── lib/                      # Utility libraries
│   │   ├── api.ts               # API client
│   │   ├── auth/                # Authentication logic
│   │   │   ├── authService.ts
│   │   │   └── providers.ts
│   │   ├── data.ts              # Data utilities
│   │   ├── dashboardApi.ts      # Dashboard API
│   │   ├── definitions.ts       # Type definitions
│   │   ├── placeholder-data.ts  # Mock data
│   │   ├── projectApi.ts        # Project API
│   │   ├── simpleDashboardApi.ts # Simple dashboard API
│   │   └── utils.ts             # Utility functions
│   ├── store/                   # State management
│   │   ├── authContext.tsx      # Auth context
│   │   └── projectContext.tsx   # Project context
│   ├── services/                # Service utilities
│   │   └── mockA2AService.ts    # Mock A2A service
│   └── types/                   # TypeScript definitions
│       ├── agent.ts
│       ├── auth.ts
│       ├── common.ts
│       ├── index.ts
│       ├── project.ts
│       └── rag.ts
├── package.json                 # Dependencies
├── next.config.ts              # Next.js configuration
├── tailwind.config.ts          # Tailwind configuration
├── tsconfig.json               # TypeScript configuration
└── README.md
```

## Core UI Components

### 1. Layout Components

#### Sidebar (`components/layout/Sidebar.tsx`)
- **Features**:
  - Hierarchical navigation with project-based filtering
  - Real-time A2A agent status indicators
  - Contextual quick actions and search
  - Responsive design with mobile drawer

### **Additional Components Found in Review:**

#### A2A Chat Interface (`app/chat/page.tsx`)
- **Advanced Features**:
  - Real-time Agent-to-Agent communication monitoring
  - WebSocket integration for live message streaming
  - Workflow-based chat sessions with multi-agent orchestration
  - Voice recording and file upload capabilities
  - A2A protocol trace visualization
  - Agent targeting and communication flow tracking
  - Export functionality for chat history
  - Citation and tool call display
  - Scratchpad visualization for agent reasoning

#### Enhanced Component Architecture
- **StandardPageLayout Integration**: Consistent layout pattern implementation
- **Advanced State Management**: Zustand + React Query for complex data flows
- **Real-time Features**: WebSocket-based live updates
- **Voice Interface**: Speech-to-text integration
- **File Handling**: Multi-file upload with progress tracking

#### Header (`components/layout/Header.tsx`)
- **Features**:
  - Global semantic search across agents, workflows, tools
  - Real-time system health indicator
  - User profile management and authentication
  - Notification center with A2A message alerts

#### PageLayout (`components/layout/PageLayout.tsx`)
- **Features**:
  - Dynamic breadcrumb navigation
  - Page-specific action buttons
  - Content grid system with responsive breakpoints

### 2. Agent Management Components

#### AgentList (`components/agents/AgentList.tsx`)
```typescript
export function AgentList() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedFramework, setSelectedFramework] = useState('all');
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  
  const { data: agents, isLoading, error } = useAgents();
  
  const filteredAgents = agents?.filter((agent: Agent) => {
    const matchesSearch = agent.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         agent.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFramework = selectedFramework === 'all' || agent.framework === selectedFramework;
    return matchesSearch && matchesFramework;
  });

  return (
    <div className="space-y-6">
      {/* Search and Filters */}
      <div className="flex gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search agents..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        <Select value={selectedFramework} onValueChange={setSelectedFramework}>
          <SelectTrigger className="w-48">
            <SelectValue placeholder="Filter by framework" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Frameworks</SelectItem>
            <SelectItem value="langchain">LangChain</SelectItem>
            <SelectItem value="crewai">CrewAI</SelectItem>
            <SelectItem value="semantic-kernel">Semantic Kernel</SelectItem>
          </SelectContent>
        </Select>
        <Button onClick={() => setIsCreateModalOpen(true)}>
          <Plus className="mr-2 h-4 w-4" />
          Create Agent
        </Button>
      </div>

      {/* Agent Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredAgents?.map((agent) => (
          <AgentCard key={agent.id} agent={agent} />
        ))}
      </div>
    </div>
  );
}
```

#### AgentCard (`components/agents/AgentCard.tsx`)
- **Features**:
  - Agent status and health indicators
  - Framework and model information
  - Quick action buttons (execute, edit, delete)
  - A2A capability badges
  - Performance metrics display

### 3. Workflow Designer Components

#### WorkflowDesigner (`components/workflows/WorkflowDesigner.tsx`)
```typescript
export function WorkflowDesigner({ 
  initialDefinition, 
  onDefinitionChange 
}: WorkflowDesignerProps) {
  const [nodes, setNodes, onNodesChange] = useNodesState(
    initialDefinition?.nodes || []
  );
  const [edges, setEdges, onEdgesChange] = useEdgesState(
    initialDefinition?.edges || []
  );
  
  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  return (
    <div className="flex h-screen">
      {/* Node Palette */}
      <div className="w-64 border-r bg-muted/50">
        <NodePalette />
      </div>
      
      {/* Flow Canvas */}
      <div className="flex-1">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          nodeTypes={nodeTypes}
          fitView
        >
          <Controls />
          <MiniMap />
          <Background variant="dots" gap={12} size={1} />
        </ReactFlow>
      </div>
    </div>
  );
}
```

### 4. A2A Protocol Visualization

#### A2ANetworkView (`components/observability/A2ANetworkView.tsx`)
- **Features**:
  - Real-time agent network topology
  - Message flow visualization
  - Agent capability mapping
  - Performance metrics overlay
  - Interactive node exploration

#### A2AMessageFlow (`components/visualization/A2AMessageFlow.tsx`)
- **Features**:
  - Real-time message tracking
  - Message routing visualization
  - Latency and performance metrics
  - Error and retry visualization

### 5. Data Visualization Components

#### NetworkDiagram (`components/visualization/NetworkDiagram.tsx`)
- **Features**:
  - Force-directed layout with customizable physics
  - Node clustering and grouping
  - Edge weight visualization
  - Interactive exploration and filtering

#### PerformanceCharts (`components/visualization/PerformanceCharts.tsx`)
- **Features**:
  - Line, bar, area, and scatter plot charts
  - Real-time data streaming
  - Zoom and pan interactions
  - Comparative analysis tools

## State Management Architecture

### 1. Zustand Store Structure
```typescript
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
```

### 2. React Query Configuration
```typescript
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
```

## API Integration

### API Client Configuration
```typescript
const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for auth
apiClient.interceptors.request.use(
  (config) => {
    const token = getAuthToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);
```

### Custom Hooks for Data Fetching
```typescript
// hooks/use-agents.ts
export function useAgents() {
  const { setAgents, setLoading, setError } = useAgentStore();
  
  return useQuery({
    queryKey: ['agents'],
    queryFn: agentApi.getAll,
    onSuccess: (data) => {
      setAgents(data);
      setLoading(false);
    },
    onError: (error) => {
      setError(error.message);
      setLoading(false);
    },
  });
}

export function useCreateAgent() {
  const queryClient = useQueryClient();
  const { addAgent } = useAgentStore();
  
  return useMutation({
    mutationFn: agentApi.create,
    onSuccess: (newAgent) => {
      addAgent(newAgent);
      queryClient.invalidateQueries(['agents']);
    },
  });
}
```

## WebSocket Integration

### Real-time Updates
```typescript
export function useWebSocket(url: string, options: UseWebSocketOptions = {}) {
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  
  const connect = () => {
    try {
      const ws = new WebSocket(url);
      wsRef.current = ws;
      
      ws.onopen = () => {
        setIsConnected(true);
        setError(null);
        options.onConnect?.();
      };
      
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        options.onMessage?.(data);
      };
      
      ws.onerror = (error) => {
        setError('WebSocket connection error');
        options.onError?.(error);
      };
      
      ws.onclose = () => {
        setIsConnected(false);
        options.onDisconnect?.();
      };
    } catch (error) {
      setError('Failed to establish WebSocket connection');
    }
  };
  
  useEffect(() => {
    connect();
    return () => {
      wsRef.current?.close();
    };
  }, [url]);
  
  return { isConnected, error, disconnect: () => wsRef.current?.close() };
}
```

## Authentication System

### Multi-Provider Authentication
- **Local Authentication**: Username/email + password with JWT
- **OAuth Providers**: GitHub, Google, Microsoft
- **Security Features**:
  - JWT token storage in httpOnly cookies
  - Automatic token refresh
  - Protected routes with authentication guards
  - Secure logout with token cleanup

### Authentication Components
```typescript
// AuthGuard component
export function AuthGuard({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();
  
  if (isLoading) {
    return <LoadingSpinner />;
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/auth/login" replace />;
  }
  
  return <>{children}</>;
}
```

## Performance Optimization

### Code Splitting
```typescript
// Lazy loading for large components
const WorkflowDesigner = lazy(() => import('./WorkflowDesigner'));
const ObservabilityDashboard = lazy(() => import('./ObservabilityDashboard'));

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

### Optimization Strategies
- **Lazy Loading**: Components are lazy-loaded where appropriate
- **Memoization**: React.memo for pure components
- **Virtual Scrolling**: For large lists and tables
- **Code Splitting**: Route-based and component-based splitting

## Responsive Design

### Breakpoint System
```typescript
const breakpoints = {
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
  '2xl': '1536px',
};
```

### Mobile-First Design
- Progressive enhancement from mobile to desktop
- Touch-friendly interactions
- Optimized navigation for small screens
- Responsive grid layouts

## Testing Strategy

### Component Testing
```typescript
// Unit tests with React Testing Library
import { render, screen, fireEvent } from '@testing-library/react';
import { AgentCard } from './AgentCard';

describe('AgentCard', () => {
  it('renders agent information correctly', () => {
    const mockAgent = {
      id: '1',
      name: 'Test Agent',
      description: 'Test description',
      status: 'active'
    };
    
    render(<AgentCard agent={mockAgent} />);
    
    expect(screen.getByText('Test Agent')).toBeInTheDocument();
    expect(screen.getByText('Test description')).toBeInTheDocument();
  });
});
```

### E2E Testing
- Playwright for end-to-end testing
- Critical user journey validation
- Cross-browser compatibility testing

## Build Configuration

### Next.js Configuration
```typescript
// next.config.ts
const nextConfig = {
  experimental: {
    appDir: true,
  },
  images: {
    domains: ['localhost', 'api.agenticai-platform.com'],
    formats: ['image/webp', 'image/avif'],
  },
  async redirects() {
    return [
      {
        source: '/',
        destination: '/dashboard',
        permanent: false,
      },
    ];
  },
};

export default nextConfig;
```

### Environment Variables
```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_GATEWAY_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
NEXTAUTH_SECRET=your-nextauth-secret
NEXTAUTH_URL=http://localhost:3000
```

## Accessibility

### WCAG 2.1 Compliance
- Semantic HTML structure
- ARIA labels and roles
- Keyboard navigation support
- Screen reader compatibility
- Color contrast compliance

### Focus Management
- Focus trapping in modals
- Skip links for navigation
- Visible focus indicators
- Logical tab order

This frontend architecture provides a modern, scalable, and accessible user interface for managing enterprise AI agents with comprehensive real-time monitoring and A2A protocol visualization capabilities.
