import React from 'react';
import { Shield } from 'lucide-react';

export const Header: React.FC = () => {
  return (
    <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-sky-500/10 text-sky-400 rounded-lg border border-sky-500/20">
            <Shield className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-slate-100 tracking-tight">APATI ASPIS</h1>
            <p className="text-xs text-slate-400">Shield Against Digital Deception</p>
          </div>
        </div>

        <nav className="flex items-center space-x-6 text-sm text-slate-300">
          <a href="#scanner" className="hover:text-sky-400 transition-colors">Scanner</a>
          <a href="#checkup" className="hover:text-sky-400 transition-colors">Security Checkup</a>
          <a href="#about" className="hover:text-sky-400 transition-colors">About</a>
        </nav>
      </div>
    </header>
  );
};
