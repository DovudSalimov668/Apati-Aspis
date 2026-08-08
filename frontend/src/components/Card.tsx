import React from 'react';

interface CardProps {
  title?: string;
  className?: string;
  children: React.ReactNode;
}

export const Card: React.FC<CardProps> = ({ title, className = '', children }) => {
  return (
    <div className={`bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl ${className}`}>
      {title && <h3 className="text-lg font-semibold text-slate-200 mb-4">{title}</h3>}
      {children}
    </div>
  );
};
