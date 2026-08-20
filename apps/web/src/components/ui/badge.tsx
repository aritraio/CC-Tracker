import * as React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const badgeVariants = cva(
  'inline-flex items-center font-bold font-mono text-xs uppercase tracking-wider px-2.5 py-0.5 border-2 border-black transition-colors select-none',
  {
    variants: {
      variant: {
        default: 'bg-muted text-ink',
        red: 'bg-bauhaus-red text-white',
        blue: 'bg-bauhaus-blue text-white',
        yellow: 'bg-bauhaus-yellow text-ink',
        green: 'bg-bauhaus-green text-white',
        outline: 'bg-white text-ink',
      },
      shape: {
        square: 'rounded-none',
        pill: 'rounded-full',
      },
    },
    defaultVariants: {
      variant: 'default',
      shape: 'square',
    },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, shape, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant, shape }), className)} {...props} />
  );
}

export { Badge, badgeVariants };
