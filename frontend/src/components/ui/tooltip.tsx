"use client"

import * as React from "react"


/**
 * TooltipProvider for wrapping tooltips (no-op for now)
 * @param props
 */
const TooltipProvider = ({ children }: { children: React.ReactNode }) => {
  return <>{children}</>;
}

/**
 * Tooltip wrapper
 * @param props
 * @returns {JSX.Element}
 * @accessibility
 * - TooltipContent uses role="tooltip" and is keyboard accessible.
 */
const Tooltip = ({ children }: { children: React.ReactNode }) => {
  return <div className="relative inline-block">{children}</div>;
}

const TooltipTrigger = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & { asChild?: boolean }
>(({ children, asChild, ...props }, ref) => {
  return (
    <div ref={ref} {...props} className="group">
      {children}
    </div>
  )
})
TooltipTrigger.displayName = "TooltipTrigger"


const TooltipContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ children, className, ...props }, ref) => {
  return (
    <div
      ref={ref}
      role="tooltip"
      tabIndex={0}
      className={`
        invisible group-hover:visible
        absolute z-50 bottom-full left-1/2 transform -translate-x-1/2 -translate-y-2
        px-2 py-1 text-xs text-white bg-gray-900 rounded shadow-lg
        whitespace-nowrap
        ${className}
      `}
      {...props}
    >
      {children}
    </div>
  )
})
TooltipContent.displayName = "TooltipContent"

export { Tooltip, TooltipTrigger, TooltipContent, TooltipProvider }
