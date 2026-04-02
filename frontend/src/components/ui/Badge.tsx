import React from 'react';

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'default' | 'violet' | 'amber' | 'emerald' | 'red';
  children: React.ReactNode;
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({ variant = 'violet', className = '', ...props }) => {
  const variants = {
    default: 'bg-zinc-800 text-zinc-300 border border-zinc-700',
    violet: 'bg-violet-500/10 text-violet-300 border border-violet-500/30',
    amber: 'bg-amber-400/10 text-amber-300 border border-amber-500/30',
    emerald: 'bg-emerald-400/10 text-emerald-300 border border-emerald-500/30',
    red: 'bg-red-400/10 text-red-300 border border-red-500/30',
  };

  return (
    <span
      className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${variants[variant]} ${className}`}
      {...props}
    />
  );
};
