import React from 'react';
import { AlertOctagon, RotateCcw } from 'lucide-react';
import { Button } from './Button';

interface ErrorStateProps {
  title?: string;
  message: string;
  onRetry?: () => void;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title = "Analysis Error",
  message,
  onRetry,
}) => {
  return (
    <div className="bg-riskHigh-bg border border-riskHigh-text/20 p-6 rounded-xl text-center flex flex-col items-center justify-center space-y-3">
      <div className="bg-riskHigh-text/10 text-riskHigh-text p-3 rounded-full">
        <AlertOctagon className="w-8 h-8" />
      </div>
      <h4 className="text-lg font-bold text-textPrimary">{title}</h4>
      <p className="text-sm text-textSecondary max-w-md">{message}</p>
      {onRetry && (
        <Button variant="secondary" size="sm" onClick={onRetry} className="mt-2">
          <RotateCcw className="w-4 h-4 mr-2" /> Try Again
        </Button>
      )}
    </div>
  );
};
