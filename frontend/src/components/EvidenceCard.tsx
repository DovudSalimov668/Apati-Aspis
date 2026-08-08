import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Database, ShieldAlert, CheckCircle2, AlertTriangle, HelpCircle } from 'lucide-react';

export type ProviderState = 'MATCH' | 'NO_MATCH' | 'UNAVAILABLE' | 'ERROR' | 'RATE_LIMITED' | 'NOT_CONFIGURED' | string;

interface EvidenceCardProps {
  providerName: string;
  state: ProviderState;
  details?: Record<string, any> | string;
}

export const EvidenceCard: React.FC<EvidenceCardProps> = ({
  providerName,
  state,
  details,
}) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const normState = (state || 'UNAVAILABLE').toUpperCase();

  const stateBadges: Record<string, { label: string; bg: string; text: string; icon: any }> = {
    MATCH: { label: 'MATCH FOUND', bg: '#FDEAEA', text: '#D14343', icon: ShieldAlert },
    NO_MATCH: { label: 'NO MATCH', bg: '#E7F7EF', text: '#1C8A5B', icon: CheckCircle2 },
    UNAVAILABLE: { label: 'UNAVAILABLE', bg: '#F1F3F5', text: '#5B6472', icon: HelpCircle },
    ERROR: { label: 'ERROR', bg: '#FFF4DF', text: '#B9821A', icon: AlertTriangle },
    RATE_LIMITED: { label: 'RATE LIMITED', bg: '#FFF4DF', text: '#B9821A', icon: AlertTriangle },
    NOT_CONFIGURED: { label: 'NOT CONFIGURED', bg: '#F1F3F5', text: '#5B6472', icon: HelpCircle },
  };

  const currentBadge = stateBadges[normState] || stateBadges.UNAVAILABLE;
  const BadgeIcon = currentBadge.icon;

  return (
    <div className="bg-surface border border-border rounded-lg overflow-hidden transition-all shadow-sm">
      <div
        onClick={() => setIsExpanded(!isExpanded)}
        className="p-4 flex items-center justify-between cursor-pointer hover:bg-slate-50 transition-colors"
      >
        <div className="flex items-center space-x-3">
          <Database className="w-5 h-5 text-brand-500 flex-shrink-0" />
          <span className="text-sm font-semibold text-textPrimary">{providerName}</span>
        </div>

        <div className="flex items-center space-x-3">
          <span
            style={{ backgroundColor: currentBadge.bg, color: currentBadge.text }}
            className="px-2.5 py-1 rounded-full text-xs font-bold flex items-center space-x-1.5 border border-black/5 uppercase tracking-wider"
          >
            <BadgeIcon className="w-3.5 h-3.5" />
            <span>{currentBadge.label}</span>
          </span>
          <button className="text-textSecondary hover:text-textPrimary">
            {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {isExpanded && (
        <div className="border-t border-border bg-slate-900 p-4 font-mono text-xs text-slate-200 overflow-x-auto">
          <pre>{typeof details === 'string' ? details : JSON.stringify(details || { state: normState }, null, 2)}</pre>
        </div>
      )}
    </div>
  );
};
