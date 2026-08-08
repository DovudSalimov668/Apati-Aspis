import React from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  helpText?: string;
  error?: string;
}

export const Input: React.FC<InputProps> = ({
  label,
  helpText,
  error,
  className = '',
  id,
  ...props
}) => {
  const inputId = id || (label ? label.toLowerCase().replace(/\s+/g, '-') : undefined);

  return (
    <div className="w-full space-y-1.5">
      {label && (
        <label htmlFor={inputId} className="block text-xs font-semibold text-textPrimary uppercase tracking-wider">
          {label}
        </label>
      )}
      <input
        id={inputId}
        className={`w-full bg-surface border rounded-lg px-4 py-2.5 text-sm text-textPrimary placeholder-textSecondary transition-colors focus:outline-none focus:ring-2 focus:ring-brand-500 ${
          error ? 'border-riskHigh-text focus:ring-riskHigh-text' : 'border-border hover:border-slate-300'
        } ${className}`}
        {...props}
      />
      {error && <p className="text-xs font-medium text-riskHigh-text">{error}</p>}
      {helpText && !error && <p className="text-xs text-textSecondary">{helpText}</p>}
    </div>
  );
};
