import React from 'react';
import { RiskLevel } from './RiskBadge';

interface ScoreDialProps {
  score: number;
  level: RiskLevel;
  size?: number;
}

export const ScoreDial: React.FC<ScoreDialProps> = ({ score, level, size = 120 }) => {
  const normLevel = (level || 'LOW').toUpperCase();
  const safeScore = Math.min(100, Math.max(0, score));

  const strokeWidth = 10;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (safeScore / 100) * circumference;

  const colorMap: Record<string, string> = {
    LOW: '#1C8A5B',
    MODERATE: '#B9821A',
    HIGH: '#D14343',
    CRITICAL: '#8F1E3B',
  };

  const dialColor = colorMap[normLevel] || '#1C8A5B';

  return (
    <div className="relative inline-flex items-center justify-center">
      <svg width={size} height={size} className="transform -rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="#E2E5EA"
          strokeWidth={strokeWidth}
          fill="transparent"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={dialColor}
          strokeWidth={strokeWidth}
          fill="transparent"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          className="transition-all duration-700 ease-out"
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
        <span className="text-3xl font-black tracking-tight text-textPrimary">{safeScore}</span>
        <span className="text-[10px] font-semibold uppercase text-textSecondary tracking-wider">/ 100</span>
      </div>
    </div>
  );
};
