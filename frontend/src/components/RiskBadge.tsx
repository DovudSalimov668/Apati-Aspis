import React from 'react';
import { ShieldCheck, ShieldAlert, ShieldX, AlertOctagon } from 'lucide-react';

export type RiskLevel = 'LOW' | 'MODERATE' | 'HIGH' | 'CRITICAL' | string;

interface RiskBadgeProps {
  level: RiskLevel;
  size?: 'sm' | 'md' | 'lg';
}

export const RiskBadge: React.FC<RiskBadgeProps> = ({ level, size = 'md' }) => {
  const normLevel = (level || 'LOW').toUpperCase();

  const configs = {
    LOW: {
      text: 'LOW RISK',
      icon: ShieldCheck,
      bgColor: '#E7F7EF',
      textColor: '#1C8A5B',
      borderColor: '#B8EBD0',
    },
    MODERATE: {
      text: 'MODERATE RISK',
      icon: ShieldAlert,
      bgColor: '#FFF4DF',
      textColor: '#B9821A',
      borderColor: '#FCE4B6',
    },
    HIGH: {
      text: 'HIGH RISK',
      icon: ShieldX,
      bgColor: '#FDEAEA',
      textColor: '#D14343',
      borderColor: '#F8C8C8',
    },
    CRITICAL: {
      text: 'CRITICAL RISK',
      icon: AlertOctagon,
      bgColor: '#F7E3E9',
      textColor: '#8F1E3B',
      borderColor: '#ECC0CC',
    },
  };

  const config = configs[normLevel as keyof typeof configs] || configs.LOW;
  const IconComponent = config.icon;

  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs font-bold gap-1 border',
    md: 'px-3 py-1 text-xs font-extrabold gap-1.5 border',
    lg: 'px-4 py-1.5 text-sm font-black gap-2 border-2',
  };

  const iconSizes = {
    sm: 'w-3.5 h-3.5',
    md: 'w-4 h-4',
    lg: 'w-5 h-5',
  };

  return (
    <span
      style={{
        backgroundColor: config.bgColor,
        color: config.textColor,
        borderColor: config.borderColor,
      }}
      className={`inline-flex items-center rounded-full tracking-wider uppercase ${sizeClasses[size]}`}
    >
      <IconComponent className={`${iconSizes[size]} flex-shrink-0`} aria-hidden="true" />
      <span>{config.text}</span>
    </span>
  );
};
