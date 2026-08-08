import React from 'react';

export const LoadingState: React.FC = () => {
  return (
    <div className="w-full space-y-4 animate-pulse p-6 bg-surface border border-border rounded-xl shadow-sm">
      <div className="flex items-center justify-between">
        <div className="h-6 bg-slate-200 rounded w-1/3"></div>
        <div className="h-6 bg-slate-200 rounded-full w-24"></div>
      </div>
      <div className="h-4 bg-slate-200 rounded w-full"></div>
      <div className="h-4 bg-slate-200 rounded w-5/6"></div>
      <div className="pt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="h-20 bg-slate-200 rounded-lg"></div>
        <div className="h-20 bg-slate-200 rounded-lg"></div>
      </div>
    </div>
  );
};
