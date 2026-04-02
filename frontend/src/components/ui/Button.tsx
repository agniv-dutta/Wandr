import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant = 'primary', size = 'md', className = '', ...props }, ref) => {
    const baseStyles = 'font-semibold rounded-full transition-all duration-300 ease-in-out flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed';

    const variants = {
      primary: 'bg-gradient-to-r from-violet-600 to-indigo-600 text-white hover:shadow-lg hover:shadow-violet-500/30 hover:scale-105',
      secondary: 'border border-zinc-700 text-zinc-300 hover:bg-zinc-800 hover:border-zinc-600',
      ghost: 'text-zinc-400 hover:text-zinc-300',
    };

    const sizes = {
      sm: 'px-4 py-2 text-sm',
      md: 'px-6 py-3 text-base',
      lg: 'px-8 py-4 text-lg',
    };

    const finalClassName = `${baseStyles} ${variants[variant]} ${sizes[size]} ${className}`;

    return <button ref={ref} className={finalClassName} {...props} />;
  }
);

Button.displayName = 'Button';
