# Frontend Components Inventory - Current Implementation

## Overview

This document provides a comprehensive inventory of all React components currently implemented in the Enterprise AI Multi-Agent Platform frontend, organized by functionality and location.

## 📁 Directory Structure

```
src/components/
├── auth/                 # Authentication components
├── chat/                 # A2A Chat components  
├── layout/               # Layout and structure components
├── navigation/           # Navigation components
└── ui/                   # Base UI components (shadcn/ui)

src/app/*/components/     # Page-specific components
```

## 🔐 Authentication Components

### `components/auth/`

#### `AuthGuard.tsx`
- **Purpose**: Route protection and authentication verification
- **Features**: 
  - Automatic redirect to login for unauthenticated users
  - Loading state management
  - Session validation
- **Usage**: Wraps protected pages/routes

#### `LoginForm.tsx`
- **Purpose**: User login interface
- **Features**:
  - Form validation
  - Error handling
  - Multiple authentication providers support
- **Integration**: Used in login pages

#### `RegisterForm.tsx`
- **Purpose**: User registration interface
- **Features**:
  - Form validation
  - Password strength validation
  - Terms and conditions
- **Integration**: Used in registration pages

## 💬 Chat Components

### `components/chat/`

#### `A2AChatInterface.tsx`
- **Purpose**: Advanced Agent-to-Agent chat interface
- **Features**:
  - Real-time WebSocket communication
  - Workflow-based chat sessions
  - Agent targeting and selection
  - Voice recording and file upload
  - A2A protocol trace visualization
  - Message streaming with typing indicators
  - Citation and tool call display
  - Chat history export
  - Connection status monitoring
- **Integration**: Main chat interface for A2A communication
- **Dependencies**: useA2AChatFastAPI hook, StandardPageLayout

## 🏗️ Layout Components

### `components/layout/`

#### `StandardPageLayout.tsx`
- **Purpose**: Consistent page layout structure
- **Features**:
  - Standardized page headers
  - Action button placement
  - Responsive grid system
  - Breadcrumb navigation
- **Variants**: default, narrow, wide, full
- **Usage**: Required for all pages

#### `PageContainer.tsx`
- **Purpose**: Basic page container wrapper
- **Features**:
  - Consistent padding and margins
  - Responsive design
- **Usage**: Alternative to StandardPageLayout for simple pages

#### `ConsistentLayout.tsx`
- **Purpose**: Ensures layout consistency across the application
- **Features**:
  - Global layout rules
  - Theme management
- **Usage**: Application-wide wrapper

### `components/navigation/`

#### `Navigation.tsx`
- **Purpose**: Main navigation component
- **Features**:
  - Hierarchical menu structure
  - Active state management
  - Responsive mobile navigation
- **Integration**: Used in main layout

## 🎨 Base UI Components (shadcn/ui)

### `components/ui/`

#### Core Components

##### `button.tsx`
- **Variants**: default, destructive, outline, secondary, ghost, link
- **Sizes**: default, sm, lg, icon
- **Features**: Loading state, disabled state, icon support

##### `input.tsx`
- **Features**: 
  - Form validation integration
  - Error states
  - Placeholder support
  - Icon integration

##### `card.tsx`
- **Components**: Card, CardHeader, CardContent, CardFooter, CardTitle, CardDescription
- **Features**: Consistent spacing, responsive design

##### `dialog.tsx`
- **Components**: Dialog, DialogContent, DialogHeader, DialogFooter, DialogTitle, DialogDescription
- **Features**: Modal management, overlay, keyboard navigation

##### `select.tsx`
- **Features**: Dropdown selection, search capability, multi-select

##### `table.tsx`
- **Components**: Table, TableHeader, TableBody, TableRow, TableCell
- **Features**: Sorting, pagination integration, responsive design

##### `tabs.tsx`
- **Components**: Tabs, TabsList, TabsTrigger, TabsContent
- **Features**: Keyboard navigation, dynamic content

#### Form Components

##### `label.tsx`
- **Features**: Form field labeling, accessibility support

##### `textarea.tsx`
- **Features**: Multi-line text input, auto-resize option

##### `switch.tsx`
- **Features**: Boolean toggle, accessible switch component

#### Feedback Components

##### `alert.tsx`
- **Variants**: default, destructive
- **Features**: Icon support, dismissible alerts

##### `badge.tsx`
- **Variants**: default, secondary, destructive, outline
- **Features**: Status indicators, counters

##### `progress.tsx`
- **Features**: Determinate and indeterminate progress

##### `skeleton.tsx`
- **Features**: Loading placeholders, animated skeletons

##### `tooltip.tsx`
- **Features**: Hover tooltips, keyboard accessible

#### Layout Components

##### `separator.tsx`
- **Features**: Horizontal and vertical separators

##### `scroll-area.tsx`
- **Features**: Custom scrollbars, smooth scrolling

#### Legacy Components (From Dashboard Template)

##### `dashboard/`
- `cards.tsx` - Dashboard metric cards
- `latest-invoices.tsx` - Recent activity display
- `nav-links.tsx` - Navigation link components
- `revenue-chart.tsx` - Chart visualization
- `sample-queries.tsx` - Sample query interface
- `sidenav.tsx` - Sidebar navigation

##### `customers/`
- `table.tsx` - Customer data table

##### `invoices/`
- `breadcrumbs.tsx` - Navigation breadcrumbs
- `buttons.tsx` - Action buttons
- `create-form.tsx` - Invoice creation form
- `edit-form.tsx` - Invoice editing form
- `pagination.tsx` - Table pagination
- `status.tsx` - Status indicators
- `table.tsx` - Invoice data table

## 📄 Page-Specific Components

### Agents Management (`app/agents/components/`)

#### `AgentCard.tsx`
- **Purpose**: Display individual agent information
- **Features**:
  - Agent status indicators
  - Capability badges
  - Action buttons (edit, delete, execute)
  - Framework and model information
- **Integration**: Used in agent listing pages

#### `AgentFilters.tsx`
- **Purpose**: Filter and search agents
- **Features**:
  - Framework filtering
  - Status filtering
  - Search functionality
- **Integration**: Agent management pages

#### `CreateAgentDialog.tsx`
- **Purpose**: Agent creation interface
- **Features**:
  - Multi-step form
  - Framework selection
  - Capability configuration
  - Validation and error handling
- **Integration**: Agent creation workflow

### Tools Management (`app/tools/components/`)

#### `AgentTemplateBuilder.tsx`
- **Purpose**: Visual agent template creation
- **Features**:
  - Drag-and-drop interface
  - Template configuration
  - Preview functionality
- **Integration**: Tool creation workflow

#### `LLMModelForm.tsx`
- **Purpose**: LLM model configuration
- **Features**:
  - Provider selection
  - Model parameter configuration
  - API key management
- **Integration**: Model setup pages

#### `PhysicalToolTester.tsx`
- **Purpose**: Test physical tool integrations
- **Features**:
  - Tool execution testing
  - Result visualization
  - Error handling
- **Integration**: Tool testing interface

#### `RAGPipelineBuilder.tsx`
- **Purpose**: Build RAG processing pipelines
- **Features**:
  - Visual pipeline creation
  - Step configuration
  - Pipeline testing
- **Integration**: RAG setup workflow

#### `ToolInstanceForm.tsx`
- **Purpose**: Create tool instances
- **Features**:
  - Instance configuration
  - Parameter setup
  - Validation
- **Integration**: Tool management

#### `ToolTemplateForm.tsx`
- **Purpose**: Create tool templates
- **Features**:
  - Template definition
  - Schema configuration
  - Template validation
- **Integration**: Tool template management

### Model Management (`app/models/components/`)

#### `EmbeddingModelForm.tsx`
- **Purpose**: Configure embedding models
- **Features**:
  - Model selection
  - Parameter configuration
  - Testing interface
- **Integration**: Embedding model setup

#### `LLMModelForm.tsx`
- **Purpose**: Configure large language models
- **Features**:
  - Provider integration
  - Model parameter tuning
  - API configuration
- **Integration**: LLM model management

### MCP Management (`app/mcp/components/`)

#### `MCPEndpointForm.tsx`
- **Purpose**: Configure MCP endpoints
- **Features**:
  - Endpoint configuration
  - Connection testing
  - Schema validation
- **Integration**: MCP setup

#### `MCPServerForm.tsx`
- **Purpose**: Register MCP servers
- **Features**:
  - Server registration
  - Capability discovery
  - Health monitoring
- **Integration**: MCP server management

#### `MCPToolTester.tsx`
- **Purpose**: Test MCP tool functionality
- **Features**:
  - Tool execution testing
  - Result validation
  - Error debugging
- **Integration**: MCP tool testing

## 🔗 Component Dependencies

### Core Dependencies
```json
{
  "@radix-ui/react-*": "^1.0.0+",
  "lucide-react": "^0.363.0",
  "class-variance-authority": "^0.7.0",
  "tailwind-merge": "^2.2.0"
}
```

### Custom Hooks Integration
- `useA2AChatFastAPI` - A2A chat functionality
- `useAgents` - Agent management
- `useWorkflows` - Workflow operations
- `useTools` - Tool management
- `useMCP` - MCP protocol operations
- `useRAG` - RAG operations
- `useDashboardData` - Dashboard data
- `useSidebarStats` - Navigation statistics

### State Management
- **Zustand**: Global state management
- **React Query**: Server state management
- **React Context**: Authentication and project context

## 📊 Component Usage Patterns

### Standardized Patterns

1. **Page Structure**: All pages use AuthGuard + StandardPageLayout
2. **Forms**: React Hook Form + Zod validation
3. **Data Fetching**: React Query hooks
4. **Styling**: Tailwind CSS with consistent design tokens
5. **Icons**: Lucide React icon library
6. **Notifications**: Custom toast system

### Accessibility Features
- WCAG 2.1 AA compliance
- Keyboard navigation
- Screen reader support
- Focus management
- Color contrast compliance

## 🚀 Performance Optimizations

- **Code Splitting**: Route-based and component-based
- **Lazy Loading**: Dynamic imports for heavy components
- **Memoization**: React.memo for pure components
- **Virtual Scrolling**: For large data sets

This component inventory reflects the current state of the frontend implementation and serves as a reference for developers working on the platform.