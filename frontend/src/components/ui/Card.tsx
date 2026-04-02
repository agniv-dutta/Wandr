import React from 'react';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  className?: string;
}

export const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className = '', ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={`bg-zinc-900/80 backdrop-blur-xl border border-zinc-700/50 rounded-2xl p-6 transition-all duration-300 ease-in-out hover:border-zinc-600/50 hover:shadow-lg hover:shadow-violet-500/20 ${className}`}
        {...props}
      />
    );
  }
);

Card.displayName = 'Card';
