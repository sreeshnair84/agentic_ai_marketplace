'use client';

import { ReactNode } from 'react';
import { cn } from '@/lib/utils';

interface ConsistentLayoutProps {
  children: ReactNode;
  className?: string;
  maxWidth?: 'default' | 'narrow' | 'wide' | 'full';
  variant?: 'default' | 'centered' | 'stretched';
}

const maxWidthClasses = {
  default: 'max-w-7xl',
  narrow: 'max-w-4xl', 
  wide: 'max-w-screen-xl',
  full: 'max-w-full'
};

/**
 * Consistent layout wrapper that provides standardized spacing and alignment
 * Works with both the old ConsistentLayout and new StandardPageLayout patterns
 * @deprecated Use StandardPageLayout for new pages
 */
export function ConsistentLayout({ 
  children, 
  className, 
  maxWidth = 'default',
  variant = 'stretched'
}: ConsistentLayoutProps) {
  return (
    <div className={cn(
      // Container with responsive max-width
      maxWidthClasses[maxWidth],
      variant === 'centered' ? 'mx-auto' : 'mx-auto',
      // Consistent responsive padding that utilizes full space
      'px-4 sm:px-6 lg:px-8',
      'py-6 sm:py-8',
      // Ensure full width utilization
      variant === 'stretched' && 'w-full',
      className
    )}>
      <div className={cn(
        'w-full',
        // Typography base
        'text-base leading-normal'
      )}>
        {children}
      </div>
    </div>
  );
}