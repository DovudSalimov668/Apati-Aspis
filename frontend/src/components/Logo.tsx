import React from 'react';
import { Shield } from 'lucide-react';

interface LogoProps {
  className?: string;
  size?: 'sm' | 'md' | 'lg';
}

export const Logo: React.FC<LogoProps> = ({ className = '', size = 'md' }) => {
  const iconSizes = { sm: 'w-5 h-5', md: 'w-6 h-6', lg: 'w-8 h-8' };
  const textSizes = { sm: 'text-base', md: 'text-lg', lg: 'text-2xl' };

  return (
    <div className={`flex items-center space-x-2.5 font-bold ${className}`}>
      <div className="bg-brand-500 text-white p-1.5 rounded-lg flex items-center justify-center shadow-sm">
        <Shield className={iconSizes[size]} />
      </div>
      <span className={`tracking-tight text-textPrimary ${textSizes[size]}`}>
        APATI <span className="text-brand-500 font-extrabold">ASPIS</span>
      </span>
    </div>
  );
};
