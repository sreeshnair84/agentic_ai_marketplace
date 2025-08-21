# Frontend Layout Standards & Architecture Guide

## Overview

This document establishes the **mandatory** layout standards, folder structure conventions, and architectural patterns that ALL modules in the Enterprise AI Platform must follow. Non-compliance with these standards will result in code rejection during review.

## Folder Structure Standards

### Module Organization Requirements
Each module under `src/app/` must follow this standardized structure:

```
/module-name/
├── components/           # Reusable components specific to this module
│   ├── ModuleCard.tsx   # PascalCase for component files
│   ├── ModuleForm.tsx
│   └── ModuleFilter.tsx
├── hooks/               # Custom hooks specific to this module (if needed)
│   ├── useModuleData.ts
│   └── useModuleFilters.ts
├── types/               # TypeScript interfaces/types for this module (if needed)
│   ├── index.ts
│   └── ModuleTypes.ts
├── utils/               # Utility functions specific to this module (if needed)
│   ├── moduleHelpers.ts
│   └── moduleValidation.ts
├── page.tsx            # Main page component (REQUIRED)
├── layout.tsx          # Module layout (OPTIONAL)
└── [sub-routes]/       # Any sub-routes/nested pages
```

### Naming Conventions

#### Files and Components
- **Component files**: PascalCase (e.g., `AgentCard.tsx`, `ToolForm.tsx`)
- **Hook files**: camelCase with `use` prefix (e.g., `useAgentData.ts`)
- **Utility files**: camelCase (e.g., `agentHelpers.ts`, `toolValidation.ts`)
- **Type files**: PascalCase (e.g., `AgentTypes.ts`, `ToolTypes.ts`)

#### Folders
- **All folders**: kebab-case for multi-word (e.g., `agent-management/`)
- **Standard folders**: `components`, `hooks`, `types`, `utils` (single words)

### Non-Compliant Modules Status

#### ❌ Tools Module (Immediate Refactoring Required)
- **Current Issues**: Components scattered in root folder
- **Files to move**: `ToolTemplateForm.tsx`, `ToolInstanceForm.tsx`, `PhysicalToolTester.tsx`, `AgentTemplateBuilder.tsx`
- **Target Structure**:
  ```
  /tools/
  ├── components/
  │   ├── ToolTemplateForm.tsx
  │   ├── ToolInstanceForm.tsx
  │   ├── PhysicalToolTester.tsx
  │   └── AgentTemplateBuilder.tsx
  └── page.tsx
  ```

#### ❌ Models Module (Immediate Refactoring Required)
- **Current Issues**: Forms in root, no component organization
- **Files to move**: `LLMModelForm.tsx`, `EmbeddingModelForm.tsx`
- **Target Structure**:
  ```
  /models/
  ├── components/
  │   ├── LLMModelForm.tsx
  │   └── EmbeddingModelForm.tsx
  └── page.tsx (needs creation)
  ```

#### ✅ Agents Module (Compliant Reference)
- **Status**: Already follows correct structure
- **Structure**: Has `components/` folder with organized components

## Architecture Principles

### 1. Standardized Page Structure
Every page must follow the exact same layout hierarchy:
- AuthGuard wrapper (security)
- StandardPageLayout (container)
- StandardSection (content grouping)
- StandardGrid/StandardCard (content organization)

### 2. Component Consistency
- Use ONLY the approved layout components
- Follow established naming conventions
- Maintain consistent spacing and typography
- Implement responsive design patterns

### 3. Accessibility First
- Semantic HTML structure
- ARIA labels and roles
- Keyboard navigation support
- Screen reader compatibility

## MANDATORY Layout Components

### 1. StandardPageLayout

**Purpose:** Primary page container with consistent spacing, breadcrumbs, and header structure.

**Required Usage:**
```tsx
import { StandardPageLayout } from '@/components/layout/StandardPageLayout';

<StandardPageLayout
  title="Page Title"                    // REQUIRED
  description="Page description"        // REQUIRED
  actions={<ActionButtons />}           // OPTIONAL
  variant="default"                     // OPTIONAL: 'default' | 'narrow' | 'wide' | 'full'
  breadcrumbs={[                        // OPTIONAL
    { label: 'Home', href: '/dashboard' },
    { label: 'Current Page' }
  ]}
>
  {/* Page content using StandardSection */}
</StandardPageLayout>
```

**Variants:**
- `default` (max-w-7xl) - Use for most pages
- `narrow` (max-w-4xl) - Use for forms and detailed views
- `wide` (max-w-screen-xl) - Use for dashboards with lots of data
- `full` (max-w-full) - Use for canvas/editor interfaces

### 2. StandardSection

**Purpose:** Groups related content within a page with consistent spacing.

**Required Usage:**
```tsx
import { StandardSection } from '@/components/layout/StandardPageLayout';

<StandardSection
  title="Section Title"                 // OPTIONAL
  description="Section description"     // OPTIONAL
  actions={<SectionActions />}          // OPTIONAL
  variant="default"                     // OPTIONAL: 'default' | 'card' | 'bordered'
>
  {/* Section content */}
</StandardSection>
```

**Variants:**
- `default` - Basic section with spacing
- `card` - Section with card background and border
- `bordered` - Section with top border separator

### 3. StandardGrid

**Purpose:** Responsive grid system for consistent layouts.

**Required Usage:**
```tsx
import { StandardGrid } from '@/components/layout/StandardPageLayout';

<StandardGrid
  cols={{ default: 1, sm: 2, md: 3, lg: 4 }}  // REQUIRED
  gap="md"                                      // OPTIONAL: 'sm' | 'md' | 'lg' | 'xl'
  responsive={true}                             // OPTIONAL: default true
>
  {/* Grid items */}
</StandardGrid>
```

**Standard Grid Patterns:**
- Stats cards: `cols={{ default: 1, sm: 2, lg: 4 }}`
- Data cards: `cols={{ default: 1, md: 2, lg: 3 }}`
- Feature cards: `cols={{ default: 1, lg: 2 }}`
- Detail panels: `cols={{ default: 1 }}`

### 4. StandardCard

**Purpose:** Consistent card component for content containers.

**Required Usage:**
```tsx
import { StandardCard } from '@/components/layout/StandardPageLayout';

<StandardCard
  title="Card Title"                    // OPTIONAL
  description="Card description"        // OPTIONAL
  actions={<CardActions />}             // OPTIONAL
  variant="default"                     // OPTIONAL: 'default' | 'elevated' | 'outlined' | 'ghost'
  padding="md"                          // OPTIONAL: 'sm' | 'md' | 'lg'
>
  {/* Card content */}
</StandardCard>
```

**Variants:**
- `default` - Standard card with border
- `elevated` - Card with shadow
- `outlined` - Card with bold border
- `ghost` - Subtle background card

## MANDATORY Page Patterns

### 1. Standard Page Template

Every page MUST follow this exact structure:

```tsx
'use client';

import { useState, useMemo } from 'react';
import { useProject } from '@/store/projectContext';
import { AuthGuard } from '@/components/auth/AuthGuard';
import { StandardPageLayout, StandardSection, StandardGrid, StandardCard } from '@/components/layout/StandardPageLayout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { 
  PlusIcon, 
  MagnifyingGlassIcon, 
  FunnelIcon
} from '@heroicons/react/24/outline';

export default function PageName() {
  // State management
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({});
  const { state: projectState } = useProject();

  // Data processing
  const filteredData = useMemo(() => {
    // Filtering logic
  }, [data, searchTerm, filters, projectState.selectedProject]);

  return (
    <AuthGuard>
      <StandardPageLayout
        title="Page Title"
        description="Page description"
        actions={
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3">
            {projectState.selectedProject && (
              <div className="flex items-center gap-2">
                <FunnelIcon className="w-4 h-4 text-blue-500" />
                <Badge variant="outline" className="border-blue-200 text-blue-700 bg-blue-50">
                  Filtered by: {projectState.selectedProject.name}
                </Badge>
              </div>
            )}
            <Button>
              <PlusIcon className="w-4 h-4 mr-2" />
              Create New
            </Button>
          </div>
        }
      >
        
        {/* Stats Section - MANDATORY for list pages */}
        <StandardSection>
          <StandardGrid cols={{ default: 1, sm: 2, lg: 4 }} gap="md">
            {/* Stats cards */}
          </StandardGrid>
        </StandardSection>

        {/* Search & Filters Section - MANDATORY for list pages */}
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
            {/* Filter components */}
          </div>
        </StandardSection>

        {/* Data Section */}
        <StandardSection>
          {filteredData.length === 0 ? (
            <StandardCard className="p-12">
              <div className="text-center">
                {/* Empty state */}
              </div>
            </StandardCard>
          ) : (
            <StandardGrid cols={{ default: 1, md: 2, lg: 3 }} gap="md">
              {filteredData.map((item) => (
                <StandardCard key={item.id}>
                  {/* Item content */}
                </StandardCard>
              ))}
            </StandardGrid>
          )}
        </StandardSection>

      </StandardPageLayout>
    </AuthGuard>
  );
}
```

### 2. Dashboard Page Pattern

```tsx
<StandardPageLayout
  title="Dashboard Title"
  description="Dashboard description"
  actions={<RefreshButton />}
>
  {/* Status Banner */}
  <StandardSection>
    <StandardCard>
      {/* System status information */}
    </StandardCard>
  </StandardSection>

  {/* Metrics Cards */}
  <StandardSection>
    <StandardGrid cols={{ default: 1, sm: 2, lg: 4 }} gap="md">
      {/* Metric cards */}
    </StandardGrid>
  </StandardSection>

  {/* Main Content */}
  <StandardSection>
    <StandardGrid cols={{ default: 1, lg: 3 }} gap="lg">
      <div className="lg:col-span-2">
        <StandardCard title="Main Content">
          {/* Primary dashboard content */}
        </StandardCard>
      </div>
      <div className="space-y-6">
        <StandardCard title="Quick Actions">
          {/* Action buttons */}
        </StandardCard>
        <StandardCard title="System Status">
          {/* Status information */}
        </StandardCard>
      </div>
    </StandardGrid>
  </StandardSection>
</StandardPageLayout>
```

### 3. Form Page Pattern

```tsx
<StandardPageLayout
  title="Create/Edit Item"
  description="Form description"
  variant="narrow"
>
  <StandardSection variant="card">
    <form onSubmit={handleSubmit}>
      {/* Form fields */}
      <div className="flex justify-end space-x-3 pt-6 border-t">
        <Button variant="outline" type="button">Cancel</Button>
        <Button type="submit">Save</Button>
      </div>
    </form>
  </StandardSection>
</StandardPageLayout>
```

## Typography Standards

### Heading Hierarchy
- **Page Titles**: `text-display-2` (30px, bold)
- **Section Titles**: `text-heading-1` (24px, semibold)
- **Card Titles**: `text-heading-2` (20px, semibold)
- **Subsection Titles**: `text-heading-3` (18px, medium)

### Body Text
- **Large Body**: `text-body-lg` (18px, normal)
- **Standard Body**: `text-body` (16px, normal)
- **Small Body**: `text-body-sm` (14px, normal)
- **Captions**: `text-caption` (12px, normal)

## Color System

### Status Colors
```tsx
// Success
className="text-green-600 bg-green-50 border-green-200 dark:text-green-400 dark:bg-green-900/20 dark:border-green-800"

// Warning  
className="text-yellow-600 bg-yellow-50 border-yellow-200 dark:text-yellow-400 dark:bg-yellow-900/20 dark:border-yellow-800"

// Error
className="text-red-600 bg-red-50 border-red-200 dark:text-red-400 dark:bg-red-900/20 dark:border-red-800"

// Info
className="text-blue-600 bg-blue-50 border-blue-200 dark:text-blue-400 dark:bg-blue-900/20 dark:border-blue-800"
```

### Framework Colors
```tsx
// LangChain: Purple
className="text-purple-600 bg-purple-50 border-purple-200"

// CrewAI: Blue  
className="text-blue-600 bg-blue-50 border-blue-200"

// Semantic Kernel: Green
className="text-green-600 bg-green-50 border-green-200"

// LlamaIndex: Orange
className="text-orange-600 bg-orange-50 border-orange-200"
```

## Spacing Standards

### Section Spacing
- Between sections: `space-y-6`
- Within sections: `space-y-4`
- Card content: `space-y-3`

### Padding Standards
- Page container: Handled by StandardPageLayout
- Card padding: `p-6` (default), `p-4` (small), `p-8` (large)
- Button spacing: `space-x-3`
- Form field spacing: `space-y-4`

## Responsive Breakpoints

### Grid Breakpoints
- `default`: Mobile (all sizes)
- `sm`: 640px and up
- `md`: 768px and up  
- `lg`: 1024px and up
- `xl`: 1280px and up
- `2xl`: 1536px and up

### Common Responsive Patterns
```tsx
// Stats cards: Stack on mobile, 2 on tablet, 4 on desktop
cols={{ default: 1, sm: 2, lg: 4 }}

// Data cards: 1 on mobile, 2 on tablet, 3 on desktop
cols={{ default: 1, md: 2, lg: 3 }}

// Feature cards: 1 on mobile/tablet, 2 on desktop
cols={{ default: 1, lg: 2 }}
```

## Component Import Standards

### Required Imports
```tsx
// Layout components (MANDATORY)
import { StandardPageLayout, StandardSection, StandardGrid, StandardCard } from '@/components/layout/StandardPageLayout';

// Authentication (MANDATORY for all pages)
import { AuthGuard } from '@/components/auth/AuthGuard';

// UI components
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';

// Icons (prefer Heroicons for consistency)
import { PlusIcon, MagnifyingGlassIcon } from '@heroicons/react/24/outline';

// State management
import { useProject } from '@/store/projectContext';
```

## Error Handling Standards

### Loading States
```tsx
if (isLoading) {
  return (
    <StandardPageLayout title="Loading...">
      <StandardSection>
        <div className="flex items-center justify-center h-64">
          <div className="text-lg">Loading data...</div>
        </div>
      </StandardSection>
    </StandardPageLayout>
  );
}
```

### Error States
```tsx
if (error) {
  return (
    <StandardPageLayout title="Error">
      <StandardSection>
        <StandardCard variant="outlined" className="border-red-200 bg-red-50">
          <div className="text-red-600">Error loading data: {error}</div>
        </StandardCard>
      </StandardSection>
    </StandardPageLayout>
  );
}
```

### Empty States
```tsx
<StandardCard className="p-12">
  <div className="text-center">
    <div className="text-gray-400 text-6xl mb-4">🔍</div>
    <h3 className="text-heading-2 text-gray-900 dark:text-white mb-2">
      No items found
    </h3>
    <p className="text-body text-gray-600 dark:text-gray-400 mb-4">
      Try adjusting your search or filters
    </p>
    <Button>Create New Item</Button>
  </div>
</StandardCard>
```

## Performance Standards

### Code Splitting
```tsx
// Lazy load heavy components
const HeavyComponent = lazy(() => import('./HeavyComponent'));

<Suspense fallback={<LoadingSpinner />}>
  <HeavyComponent />
</Suspense>
```

### Memoization
```tsx
// Memoize expensive computations
const filteredData = useMemo(() => {
  return data.filter(/* filtering logic */);
}, [data, searchTerm, filters]);

// Memoize callback functions
const handleAction = useCallback((id: string) => {
  // action logic
}, [dependencies]);
```

## Testing Standards

### Component Testing
```tsx
describe('PageComponent', () => {
  it('renders with standard layout', () => {
    render(<PageComponent />);
    expect(screen.getByRole('main')).toBeInTheDocument();
    expect(screen.getByText('Page Title')).toBeInTheDocument();
  });

  it('displays filtered data correctly', () => {
    // Test filtering logic
  });
});
```

## Accessibility Standards

### Semantic HTML
- Use proper heading hierarchy (h1 → h2 → h3)
- Include ARIA labels for interactive elements
- Provide alt text for images
- Use semantic HTML elements (main, section, article, nav)

### Keyboard Navigation
- All interactive elements must be keyboard accessible
- Provide focus indicators
- Implement logical tab order
- Support escape key for modals/dropdowns

### Screen Reader Support
- Use descriptive text for links and buttons
- Provide ARIA labels for complex interactions
- Include status announcements for dynamic content

## Code Review Checklist

Before submitting code, verify:

- [ ] Uses StandardPageLayout as root container
- [ ] Wrapped in AuthGuard
- [ ] Follows established section structure
- [ ] Uses consistent typography classes
- [ ] Implements responsive design patterns
- [ ] Includes proper error/loading/empty states
- [ ] Follows naming conventions
- [ ] Includes accessibility features
- [ ] Optimized for performance
- [ ] Includes proper TypeScript types

## Non-Compliance Consequences

**Code that does not follow these standards will be rejected during code review.**

Common violations:
- Using custom layout components instead of Standard* components
- Inconsistent spacing or typography
- Missing responsive design
- Poor accessibility implementation
- Non-standard error handling
- Inconsistent component patterns

**Remember: Consistency is more important than individual preferences. Follow the standards exactly.**
