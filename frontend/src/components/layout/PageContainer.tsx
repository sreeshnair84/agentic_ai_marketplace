'use client';

import { ReactNode } from 'react';
import { cn } from '@/lib/utils';

interface PageContainerProps {
  children: ReactNode;
  className?: string;
  title?: string;
  description?: string;
  actions?: ReactNode;
  maxWidth?: 'sm' | 'md' | 'lg' | 'xl' | '2xl' | '7xl' | 'full';
  spacing?: 'none' | 'sm' | 'md' | 'lg';
  padding?: 'none' | 'sm' | 'md' | 'lg';
}

const maxWidthClasses = {
  sm: 'max-w-screen-sm',
  md: 'max-w-screen-md', 
  lg: 'max-w-screen-lg',
  xl: 'max-w-screen-xl',
  '2xl': 'max-w-screen-2xl',
  '7xl': 'max-w-7xl',
  full: 'max-w-full'
};

const spacingClasses = {
  none: 'space-y-0',
  sm: 'space-y-4',
  md: 'space-y-6', 
  lg: 'space-y-8'
};

const paddingClasses = {
  none: '',
  sm: 'px-4 py-4 sm:px-6 sm:py-6',
  md: 'px-4 py-6 sm:px-6 sm:py-8',
  lg: 'px-4 py-8 sm:px-6 sm:py-12 lg:px-8'
};

export function PageContainer({ 
  children, 
  className,
  title,
  description,
  actions,
  maxWidth = '7xl',
  spacing = 'md',
  padding = 'md'
}: PageContainerProps) {
  return (
    <div className={cn(
      'min-h-full w-full',
      className
    )}>
      <div className={cn(
        'mx-auto',
        maxWidthClasses[maxWidth],
        paddingClasses[padding]
      )}>
        {/* Page Header */}
        {(title || actions) && (
          <div className="mb-6 sm:mb-8">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
              {title && (
                <div className="min-w-0 flex-1">
                  <h1 className="text-display-2 text-gray-900 dark:text-white">
                    {title}
                  </h1>
                  {description && (
                    <p className="mt-2 text-body text-gray-600 dark:text-gray-400 max-w-3xl">
                      {description}
                    </p>
                  )}
                </div>
              )}
              {actions && (
                <div className="flex flex-shrink-0 flex-wrap items-center gap-3">
                  {actions}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Page Content */}
        <div className={spacingClasses[spacing]}>
          {children}
        </div>
      </div>
    </div>
  );
}

interface PageSectionProps {
  children: ReactNode;
  className?: string;
  title?: string;
  description?: string;
  actions?: ReactNode;
  spacing?: 'none' | 'sm' | 'md' | 'lg';
}

export function PageSection({ 
  children, 
  className,
  title,
  description, 
  actions,
  spacing = 'md'
}: PageSectionProps) {
  return (
    <section className={cn('w-full', spacingClasses[spacing], className)}>
      {(title || actions) && (
        <div className="mb-4 sm:mb-6">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
            {title && (
              <div className="min-w-0 flex-1">
                <h2 className="text-heading-1 text-gray-900 dark:text-white">
                  {title}
                </h2>
                {description && (
                  <p className="mt-1 text-body-sm text-gray-600 dark:text-gray-400">
                    {description}
                  </p>
                )}
              </div>
            )}
            {actions && (
              <div className="flex flex-shrink-0 items-center gap-3">
                {actions}
              </div>
            )}
          </div>
        </div>
      )}
      <div>
        {children}
      </div>
    </section>
  );
}

interface PageGridProps {
  children: ReactNode;
  className?: string;
  cols?: {
    default?: number;
    sm?: number;
    md?: number;
    lg?: number;
    xl?: number;
  };
  gap?: 'sm' | 'md' | 'lg' | 'xl';
}

const gapClasses = {
  sm: 'gap-4',
  md: 'gap-6',
  lg: 'gap-8',
  xl: 'gap-10'
};

export function PageGrid({ 
  children, 
  className,
  cols = { default: 1, md: 2, lg: 3 },
  gap = 'md' 
}: PageGridProps) {
  const gridColsClasses = [
    cols.default && `grid-cols-${cols.default}`,
    cols.sm && `sm:grid-cols-${cols.sm}`,
    cols.md && `md:grid-cols-${cols.md}`,
    cols.lg && `lg:grid-cols-${cols.lg}`,
    cols.xl && `xl:grid-cols-${cols.xl}`
  ].filter(Boolean).join(' ');

  return (
    <div className={cn(
      'grid w-full',
      gridColsClasses,
      gapClasses[gap],
      className
    )}>
      {children}
    </div>
  );
}