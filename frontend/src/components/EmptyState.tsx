import React from 'react';
import { Inbox } from 'lucide-react';

interface EmptyStateProps {
  title?: string;
  description?: string;
  icon?: React.ElementType;
  action?: React.ReactNode;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title = "No Scan History Found",
  description = "Analyze suspicious URLs, text messages, QR codes, or passwords to populate your safety log.",
  icon: Icon = Inbox,
  action,
}) => {
  return (
    <div className="bg-surface border border-border rounded-xl p-10 text-center flex flex-col items-center justify-center space-y-3">
      <div className="bg-slate-100 text-textSecondary p-4 rounded-full">
        <Icon className="w-8 h-8" />
      </div>
      <h4 className="text-base font-bold text-textPrimary">{title}</h4>
      <p className="text-sm text-textSecondary max-w-sm leading-relaxed">{description}</p>
      {action && <div className="pt-2">{action}</div>}
    </div>
  );
};
