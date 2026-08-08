import React from 'react';
import { Search, ShieldAlert, BookOpen } from 'lucide-react';

export const StepIndicator: React.FC = () => {
  const steps = [
    {
      num: '01',
      title: '1. Check',
      desc: 'Paste suspicious URLs, messages, QR codes, screenshots, or passwords.',
      icon: Search,
    },
    {
      num: '02',
      title: '2. Analyze',
      desc: 'Multi-layer heuristics, threat intelligence DBs, and SSRF validation run in real time.',
      icon: ShieldAlert,
    },
    {
      num: '03',
      title: '3. Understand',
      desc: 'Receive clear, non-technical risk explanations and targeted safety action steps.',
      icon: BookOpen,
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 my-12">
      {steps.map((step) => {
        const Icon = step.icon;
        return (
          <div key={step.num} className="bg-surface border border-border rounded-xl p-6 shadow-sm flex flex-col justify-between">
            <div className="flex items-center justify-between mb-4">
              <div className="bg-brand-50 text-brand-600 p-3 rounded-lg font-bold">
                <Icon className="w-5 h-5" />
              </div>
              <span className="text-2xl font-black text-slate-300">{step.num}</span>
            </div>
            <div>
              <h4 className="text-base font-bold text-textPrimary mb-1">{step.title}</h4>
              <p className="text-xs text-textSecondary leading-relaxed">{step.desc}</p>
            </div>
          </div>
        );
      })}
    </div>
  );
};
