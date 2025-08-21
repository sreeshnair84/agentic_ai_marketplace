'use client';

import { ReactNode } from 'react';
import { cn } from '@/lib/utils';

interface StandardPageLayoutProps {
  children: ReactNode;
  className?: string;
  title?: string;
  description?: string;
  actions?: ReactNode;
  breadcrumbs?: Array<{ label: string; href?: string }>;
  variant?: 'default' | 'narrow' | 'wide' | 'full';
}

const variantClasses = {
  default: 'max-w-7xl',
  narrow: 'max-w-4xl',
  wide: 'max-w-screen-xl',
  full: 'max-w-full'
};

export function StandardPageLayout({
  children,
  className,
  title,
  description,
  actions,
  breadcrumbs,
  variant = 'default'
}: StandardPageLayoutProps) {
  return (
    <div className={cn('min-h-full bg-gray-50 dark:bg-gray-900', className)}>
      <div className={cn(
        'mx-auto px-4 py-6 sm:px-6 sm:py-8 lg:px-8',
        variantClasses[variant]
      )}>
        {/* Breadcrumbs */}
        {breadcrumbs && breadcrumbs.length > 0 && (
          <nav className="mb-4 sm:mb-6" aria-label="Breadcrumb">
            <ol className="flex items-center space-x-2 text-caption text-gray-500 dark:text-gray-400">
              {breadcrumbs.map((crumb, index) => (
                <li key={index} className="flex items-center">
                  {index > 0 && (
                    <svg className="mr-2 h-3 w-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                    </svg>
                  )}
                  {crumb.href ? (
                    <a 
                      href={crumb.href}
                      className="hover:text-gray-700 dark:hover:text-gray-300 transition-colors"
                    >
                      {crumb.label}
                    </a>
                  ) : (
                    <span className="text-gray-900 dark:text-white font-medium">
                      {crumb.label}
                    </span>
                  )}
                </li>
              ))}
            </ol>
          </nav>
        )}

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
        <div className="space-y-6">
          {children}
        </div>
      </div>
    </div>
  );
}

interface StandardSectionProps {
  children: ReactNode;
  className?: string;
  title?: string;
  description?: string;
  actions?: ReactNode;
  variant?: 'default' | 'card' | 'bordered';
}

export function StandardSection({
  children,
  className,
  title,
  description,
  actions,
  variant = 'default'
}: StandardSectionProps) {
  const sectionContent = (
    <>
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
    </>
  );

  if (variant === 'card') {
    return (
      <section className={cn(
        'bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6',
        className
      )}>
        {sectionContent}
      </section>
    );
  }

  if (variant === 'bordered') {
    return (
      <section className={cn(
        'border-t border-gray-200 dark:border-gray-700 pt-6',
        className
      )}>
        {sectionContent}
      </section>
    );
  }

  return (
    <section className={cn('w-full', className)}>
      {sectionContent}
    </section>
  );
}

interface StandardGridProps {
  children: ReactNode;
  className?: string;
  cols?: {
    default?: number;
    sm?: number;
    md?: number;
    lg?: number;
    xl?: number;
    '2xl'?: number;
  };
  gap?: 'sm' | 'md' | 'lg' | 'xl';
  responsive?: boolean;
}

export function StandardGrid({
  children,
  className,
  cols = { default: 1, md: 2, lg: 3 },
  gap = 'md',
  responsive = true
}: StandardGridProps) {
  const gapClasses = {
    sm: 'gap-4',
    md: 'gap-6',
    lg: 'gap-8',
    xl: 'gap-10'
  };

  const getGridCols = () => {
    if (!responsive) {
      return `grid-cols-${cols.default || 1}`;
    }

    return [
      cols.default && `grid-cols-${cols.default}`,
      cols.sm && `sm:grid-cols-${cols.sm}`,
      cols.md && `md:grid-cols-${cols.md}`,
      cols.lg && `lg:grid-cols-${cols.lg}`,
      cols.xl && `xl:grid-cols-${cols.xl}`,
      cols['2xl'] && `2xl:grid-cols-${cols['2xl']}`
    ].filter(Boolean).join(' ');
  };

  return (
    <div className={cn(
      'grid w-full',
      getGridCols(),
      gapClasses[gap],
      className
    )}>
      {children}
    </div>
  );
}

interface StandardCardProps {
  children: ReactNode;
  className?: string;
  title?: string;
  description?: string;
  actions?: ReactNode;
  variant?: 'default' | 'elevated' | 'outlined' | 'ghost';
  padding?: 'sm' | 'md' | 'lg';
}

export function StandardCard({
  children,
  className,
  title,
  description,
  actions,
  variant = 'default',
  padding = 'md'
}: StandardCardProps) {
  const variantClasses = {
    default: 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700',
    elevated: 'bg-white dark:bg-gray-800 shadow-lg border border-gray-200 dark:border-gray-700',
    outlined: 'bg-transparent border-2 border-gray-200 dark:border-gray-700',
    ghost: 'bg-gray-50 dark:bg-gray-800/50 border border-gray-100 dark:border-gray-700/50'
  };

  const paddingClasses = {
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8'
  };

  return (
    <div className={cn(
      'rounded-lg transition-colors',
      variantClasses[variant],
      paddingClasses[padding],
      className
    )}>
      {(title || actions) && (
        <div className="mb-4">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
            {title && (
              <div className="min-w-0 flex-1">
                <h3 className="text-heading-2 text-gray-900 dark:text-white">
                  {title}
                </h3>
                {description && (
                  <p className="mt-1 text-body-sm text-gray-600 dark:text-gray-400">
                    {description}
                  </p>
                )}
              </div>
            )}
            {actions && (
              <div className="flex flex-shrink-0 items-center gap-2">
                {actions}
              </div>
            )}
          </div>
        </div>
      )}
      {children}
    </div>
  );
}
