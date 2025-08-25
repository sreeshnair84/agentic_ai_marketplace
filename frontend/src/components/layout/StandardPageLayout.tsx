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
  variant?: 'default' | 'narrow' | 'wide' | 'full' | 'adaptive';
}

const variantClasses = {
  default: 'max-w-7xl 2xl:max-w-full 2xl:px-8',
  narrow: 'max-w-4xl xl:max-w-5xl',
  wide: 'max-w-screen-xl 2xl:max-w-full 2xl:px-12',
  full: 'max-w-full',
  adaptive: 'max-w-7xl xl:max-w-screen-xl 2xl:max-w-full'
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
    <div className={cn('min-h-full bg-gradient-to-br from-gray-50 via-white to-gray-50/80 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900/80', className)}>
      <div className={cn(
        'mx-auto px-4 py-6 sm:px-6 sm:py-8 lg:px-8 xl:px-10 2xl:px-16',
        variantClasses[variant]
      )}>
        {/* Enhanced Breadcrumbs */}
        {breadcrumbs && breadcrumbs.length > 0 && (
          <nav className="mb-6 sm:mb-8" aria-label="Breadcrumb">
            <div className="flex items-center gap-3 p-4 bg-white/80 dark:bg-gray-800/80 rounded-xl backdrop-blur-sm border border-gray-200/50 dark:border-gray-600/50 shadow-sm">
              <ol className="flex items-center space-x-3 text-sm text-gray-500 dark:text-gray-400">
                {breadcrumbs.map((crumb, index) => (
                  <li key={index} className="flex items-center">
                    {index > 0 && (
                      <svg className="mr-3 h-4 w-4 flex-shrink-0 text-gray-300 dark:text-gray-600" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                      </svg>
                    )}
                    {crumb.href ? (
                      <a 
                        href={crumb.href}
                        className="hover:text-blue-600 dark:hover:text-blue-400 transition-all duration-150 px-2 py-1 rounded-lg hover:bg-blue-50 dark:hover:bg-blue-900/20 font-medium"
                      >
                        {crumb.label}
                      </a>
                    ) : (
                      <span className="text-gray-900 dark:text-white font-semibold px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded-lg">
                        {crumb.label}
                      </span>
                    )}
                  </li>
                ))}
              </ol>
            </div>
          </nav>
        )}

        {/* Enhanced Page Header */}
        {(title || actions) && (
          <div className="mb-8 sm:mb-10">
            <div className="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
              {title && (
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-4 mb-3">
                    <div className="w-1.5 h-12 bg-gradient-to-b from-blue-500 to-purple-600 rounded-full shadow-sm"></div>
                    <div>
                      <h1 className="text-3xl xl:text-4xl font-bold bg-gradient-to-r from-gray-900 via-gray-800 to-gray-700 dark:from-white dark:via-gray-100 dark:to-gray-300 bg-clip-text text-transparent leading-tight">
                        {title}
                      </h1>
                      {description && (
                        <p className="mt-3 text-lg text-gray-600 dark:text-gray-400 max-w-4xl leading-relaxed">
                          {description}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              )}
              {actions && (
                <div className="flex flex-shrink-0 flex-wrap items-center gap-4">
                  {actions}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Enhanced Page Content */}
        <div className="space-y-8 xl:space-y-10">
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
        <div className="mb-6 sm:mb-8">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
            {title && (
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <div className="w-1 h-8 bg-gradient-to-b from-blue-500 to-purple-600 rounded-full"></div>
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                    {title}
                  </h2>
                </div>
                {description && (
                  <p className="mt-2 text-base text-gray-600 dark:text-gray-400 max-w-3xl leading-relaxed">
                    {description}
                  </p>
                )}
              </div>
            )}
            {actions && (
              <div className="flex flex-shrink-0 flex-wrap items-center gap-4">
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
        'bg-white/80 dark:bg-gray-800/80 rounded-2xl border border-gray-200/50 dark:border-gray-700/50 p-8 xl:p-10 backdrop-blur-sm shadow-lg hover:shadow-xl transition-shadow duration-300',
        className
      )}>
        {sectionContent}
      </section>
    );
  }

  if (variant === 'bordered') {
    return (
      <section className={cn(
        'border-t border-gray-200/50 dark:border-gray-700/50 pt-8 xl:pt-10',
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
    sm: 'gap-4 xl:gap-5',
    md: 'gap-6 xl:gap-8',
    lg: 'gap-8 xl:gap-10',
    xl: 'gap-10 xl:gap-12'
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
    default: 'bg-white/90 dark:bg-gray-800/90 border border-gray-200/50 dark:border-gray-700/50 backdrop-blur-sm shadow-sm hover:shadow-lg hover:bg-white dark:hover:bg-gray-800',
    elevated: 'bg-white/95 dark:bg-gray-800/95 shadow-xl border border-gray-200/50 dark:border-gray-700/50 backdrop-blur-md hover:shadow-2xl hover:scale-[1.01]',
    outlined: 'bg-white/60 dark:bg-gray-800/60 border-2 border-gray-300/70 dark:border-gray-600/70 backdrop-blur-sm hover:border-blue-300 dark:hover:border-blue-600 hover:bg-white/80 dark:hover:bg-gray-800/80',
    ghost: 'bg-gray-50/80 dark:bg-gray-800/40 border border-gray-200/40 dark:border-gray-700/40 backdrop-blur-sm hover:bg-gray-100/60 dark:hover:bg-gray-700/60'
  };

  const paddingClasses = {
    sm: 'p-4 xl:p-5',
    md: 'p-6 xl:p-8',
    lg: 'p-8 xl:p-10'
  };

  return (
    <div className={cn(
      'rounded-2xl transition-all duration-300 hover:transform group',
      variantClasses[variant],
      paddingClasses[padding],
      className
    )}>
      {(title || actions) && (
        <div className="mb-6">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
            {title && (
              <div className="min-w-0 flex-1">
                <h3 className="text-xl font-bold text-gray-900 dark:text-white group-hover:text-blue-900 dark:group-hover:text-blue-100 transition-colors">
                  {title}
                </h3>
                {description && (
                  <p className="mt-2 text-base text-gray-600 dark:text-gray-400 leading-relaxed">
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
      {children}
    </div>
  );
}
