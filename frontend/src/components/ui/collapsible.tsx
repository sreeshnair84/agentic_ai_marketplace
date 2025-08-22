"use client"

import React, { createContext, useContext, useState } from 'react'
import { cn } from '@/lib/utils'

// Simple collapsible implementation without Radix UI dependency
interface CollapsibleContextType {
  open: boolean
  setOpen: (open: boolean) => void
}

const CollapsibleContext = createContext<CollapsibleContextType | null>(null)

interface CollapsibleProps {
  children: React.ReactNode
  open?: boolean
  onOpenChange?: (open: boolean) => void
  defaultOpen?: boolean
  className?: string
}

const Collapsible = React.forwardRef<HTMLDivElement, CollapsibleProps>(
  ({ children, open: controlledOpen, onOpenChange, defaultOpen = false, className, ...props }, ref) => {
    const [internalOpen, setInternalOpen] = useState(defaultOpen)
    const open = controlledOpen !== undefined ? controlledOpen : internalOpen
    
    const setOpen = (newOpen: boolean) => {
      if (controlledOpen === undefined) {
        setInternalOpen(newOpen)
      }
      onOpenChange?.(newOpen)
    }
    
    return (
      <CollapsibleContext.Provider value={{ open, setOpen }}>
        <div ref={ref} className={className} {...props}>
          {children}
        </div>
      </CollapsibleContext.Provider>
    )
  }
)
Collapsible.displayName = "Collapsible"

const CollapsibleTrigger = React.forwardRef<
  HTMLButtonElement,
  React.ButtonHTMLAttributes<HTMLButtonElement>
>(({ children, className, onClick, ...props }, ref) => {
  const context = useContext(CollapsibleContext)
  if (!context) {
    throw new Error('CollapsibleTrigger must be used within Collapsible')
  }
  
  const { open, setOpen } = context
  
  return (
    <button
      ref={ref}
      onClick={(e) => {
        setOpen(!open)
        onClick?.(e)
      }}
      className={cn("cursor-pointer", className)}
      {...props}
    >
      {children}
    </button>
  )
})
CollapsibleTrigger.displayName = "CollapsibleTrigger"

const CollapsibleContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ children, className, ...props }, ref) => {
  const context = useContext(CollapsibleContext)
  if (!context) {
    throw new Error('CollapsibleContent must be used within Collapsible')
  }
  
  const { open } = context
  
  if (!open) {
    return null
  }
  
  return (
    <div
      ref={ref}
      className={cn("animate-in slide-in-from-top-1 duration-200", className)}
      {...props}
    >
      {children}
    </div>
  )
})
CollapsibleContent.displayName = "CollapsibleContent"

export { Collapsible, CollapsibleTrigger, CollapsibleContent }