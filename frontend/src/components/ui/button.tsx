import * as React from "react";
import { Slot } from "@radix-ui/react-slot"
import clsx from 'clsx';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
  variant?: "default" | "destructive" | "outline" | "secondary" | "ghost" | "link";
  size?: "default" | "sm" | "lg" | "icon";
  asChild?: boolean;
}

export function Button({ 
  children, 
  className, 
  variant = "default", 
  size = "default",
  asChild = false,
  ...rest 
}: ButtonProps) {
  const Comp = asChild ? Slot : "button"
  
  return (
    <Comp
      {...rest}
      className={clsx(
        'inline-flex items-center justify-center whitespace-nowrap rounded-lg text-sm font-medium transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 disabled:pointer-events-none disabled:opacity-50',
        {
          // Variants
          'bg-blue-500 text-white hover:bg-blue-400 focus-visible:outline-blue-500 active:bg-blue-600': variant === "default",
          'bg-red-500 text-white hover:bg-red-400 focus-visible:outline-red-500 active:bg-red-600': variant === "destructive",
          'border border-gray-300 bg-white text-gray-900 hover:bg-gray-50 focus-visible:outline-gray-500': variant === "outline",
          'bg-gray-100 text-gray-900 hover:bg-gray-200 focus-visible:outline-gray-500': variant === "secondary",
          'text-gray-900 hover:bg-gray-100 focus-visible:outline-gray-500': variant === "ghost",
          'text-blue-500 underline-offset-4 hover:underline focus-visible:outline-blue-500': variant === "link",
        },
        {
          // Sizes
          'h-10 px-4 py-2': size === "default",
          'h-9 px-3 text-xs': size === "sm",
          'h-11 px-8': size === "lg",
          'h-10 w-10': size === "icon",
        },
        className,
      )}
    >
      {children}
    </Comp>
  );
}
