import * as React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const buttonVariants = cva(
  'inline-flex items-center justify-center font-bold uppercase tracking-wider transition-all duration-100 focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-bauhaus-yellow disabled:pointer-events-none disabled:opacity-50 select-none',
  {
    variants: {
      variant: {
        primary:
          'bg-bauhaus-red text-white border-2 md:border-4 border-black shadow-bauhaus-sm hover:-translate-x-0.5 hover:-translate-y-0.5 hover:shadow-bauhaus-md active:translate-x-1 active:translate-y-1 active:shadow-none',
        secondary:
          'bg-bauhaus-blue text-white border-2 md:border-4 border-black shadow-bauhaus-sm hover:-translate-x-0.5 hover:-translate-y-0.5 hover:shadow-bauhaus-md active:translate-x-1 active:translate-y-1 active:shadow-none',
        yellow:
          'bg-bauhaus-yellow text-black border-2 md:border-4 border-black shadow-bauhaus-sm hover:-translate-x-0.5 hover:-translate-y-0.5 hover:shadow-bauhaus-md active:translate-x-1 active:translate-y-1 active:shadow-none focus-visible:ring-bauhaus-red',
        outline:
          'bg-white text-black border-2 md:border-4 border-black shadow-bauhaus-sm hover:-translate-x-0.5 hover:-translate-y-0.5 hover:shadow-bauhaus-md active:translate-x-1 active:translate-y-1 active:shadow-none',
        dark:
          'bg-ink text-white border-2 md:border-4 border-black shadow-bauhaus-sm hover:-translate-x-0.5 hover:-translate-y-0.5 hover:shadow-bauhaus-md active:translate-x-1 active:translate-y-1 active:shadow-none shadow-bauhaus-yellow',
        ghost:
          'border-none text-black hover:bg-muted active:bg-muted/80',
      },
      size: {
        sm: 'h-9 px-3 text-xs',
        md: 'h-11 px-5 text-sm',
        lg: 'h-14 px-8 text-base',
        icon: 'h-11 w-11 p-0',
      },
      shape: {
        square: 'rounded-none',
        pill: 'rounded-full',
      },
    },
    defaultVariants: {
      variant: 'primary',
      size: 'md',
      shape: 'square',
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, shape, ...props }, ref) => {
    return (
      <button
        className={cn(buttonVariants({ variant, size, shape, className }))}
        ref={ref}
        {...props}
      />
    );
  }
);
Button.displayName = 'Button';

export { Button, buttonVariants };
