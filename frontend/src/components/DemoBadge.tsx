import React from 'react';
import { AlertTriangle } from 'lucide-react';

export const DemoBadge: React.FC = () => {
  return (
    <div className="bg-amber-500 text-white font-black text-xs px-3 py-1.5 rounded-md inline-flex items-center space-x-1.5 shadow-sm border border-amber-600 uppercase tracking-widest my-2">
      <AlertTriangle className="w-4 h-4" />
      <span>DEMO / SIMULATED RESULT</span>
    </div>
  );
};
