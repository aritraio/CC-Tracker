import * as React from 'react';
import { cn } from '@/lib/utils';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  shapeCorner?: 'circle' | 'square' | 'triangle' | 'none';
}

const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className, shapeCorner = 'none', children, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(
        'bg-white text-ink border-2 md:border-4 border-black shadow-bauhaus-md md:shadow-bauhaus-lg relative transition-transform duration-150',
        className
      )}
      {...props}
    >
      {shapeCorner === 'circle' && (
        <div
          className="absolute top-4 right-4 w-4 h-4 rounded-full bg-bauhaus-red border-2 border-black"
          aria-hidden="true"
        />
      )}
      {shapeCorner === 'square' && (
        <div
          className="absolute top-4 right-4 w-4 h-4 rounded-none bg-bauhaus-blue border-2 border-black"
          aria-hidden="true"
        />
      )}
      {shapeCorner === 'triangle' && (
        <div
          className="absolute top-4 right-4 w-4 h-4 bg-bauhaus-yellow bauhaus-clip-triangle"
          aria-hidden="true"
        />
      )}
      {children}
    </div>
  )
);
Card.displayName = 'Card';

const CardHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn('flex flex-col space-y-1.5 p-5 md:p-6', className)}
    {...props}
  />
));
CardHeader.displayName = 'CardHeader';

const CardTitle = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => (
  <h3
    ref={ref}
    className={cn(
      'font-black text-xl md:text-2xl uppercase tracking-tight leading-none text-ink',
      className
    )}
    {...props}
  />
));
CardTitle.displayName = 'CardTitle';

const CardDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn('text-sm text-ink/75 font-medium leading-relaxed', className)}
    {...props}
  />
));
CardDescription.displayName = 'CardDescription';

const CardContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div ref={ref} className={cn('p-5 md:p-6 pt-0', className)} {...props} />
));
CardContent.displayName = 'CardContent';

const CardFooter = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn('flex items-center p-5 md:p-6 pt-0', className)}
    {...props}
  />
));
CardFooter.displayName = 'CardFooter';

export { Card, CardHeader, CardFooter, CardTitle, CardDescription, CardContent };
