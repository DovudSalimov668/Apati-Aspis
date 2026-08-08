import React from 'react';
import { Info, CheckCircle2, AlertTriangle, AlertCircle } from 'lucide-react';

interface AlertProps {
  type?: 'info' | 'success' | 'warning' | 'error';
  title?: string;
  children: React.ReactNode;
  className?: string;
}

export const Alert: React.FC<AlertProps> = ({
  type = 'info',
  title,
  children,
  className = '',
}) => {
  const configs = {
    info: {
      bgColor: '#EEF4FF',
      textColor: '#1B36A8',
      borderColor: '#C3D7FF',
      icon: Info,
    },
    success: {
      bgColor: '#E7F7EF',
      textColor: '#1C8A5B',
      borderColor: '#B8EBD0',
      icon: CheckCircle2,
    },
    warning: {
      bgColor: '#FFF4DF',
      textColor: '#B9821A',
      borderColor: '#FCE4B6',
      icon: AlertTriangle,
    },
    error: {
      bgColor: '#FDEAEA',
      textColor: '#D14343',
      borderColor: '#F8C8C8',
      icon: AlertCircle,
    },
  };

  const config = configs[type];
  const IconComponent = config.icon;

  return (
    <div
      style={{
        backgroundColor: config.bgColor,
        color: config.textColor,
        borderColor: config.borderColor,
      }}
      className={`p-4 rounded-xl border flex items-start space-x-3 text-sm font-medium shadow-sm ${className}`}
      role="alert"
    >
      <IconComponent className="w-5 h-5 flex-shrink-0 mt-0.5" aria-hidden="true" />
      <div className="flex-1">
        {title && <h5 className="font-bold text-base mb-1 tracking-tight">{title}</h5>}
        <div className="leading-relaxed opacity-95">{children}</div>
      </div>
    </div>
  );
};
