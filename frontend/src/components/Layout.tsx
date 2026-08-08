import React from 'react';
import { Logo } from './Logo';
import { DisclaimerFooter } from './DisclaimerFooter';
import { Search, KeyRound, ShieldCheck, History, Info } from 'lucide-react';

interface LayoutProps {
  children: React.ReactNode;
  activeRoute: string;
  onNavigate: (route: string) => void;
}

export const Layout: React.FC<LayoutProps> = ({ children, activeRoute, onNavigate }) => {
  const navItems = [
    { id: 'home', label: 'Home / Scanner', icon: Search },
    { id: 'password-check', label: 'Password Check', icon: KeyRound },
    { id: 'checkup', label: 'Security Checkup', icon: ShieldCheck },
    { id: 'history', label: 'Scan History', icon: History },
    { id: 'about', label: 'About Product', icon: Info },
  ];

  return (
    <div className="min-h-screen bg-bg text-textPrimary flex flex-col md:flex-row font-sans">
      {/* Desktop Sidebar Navigation */}
      <aside className="hidden md:flex md:w-64 bg-surface border-r border-border flex-col justify-between p-6 shrink-0 shadow-sm">
        <div className="space-y-8">
          <Logo size="md" />

          <nav className="space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeRoute === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => onNavigate(item.id)}
                  className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-brand-50 text-brand-600 font-semibold'
                      : 'text-textSecondary hover:text-textPrimary hover:bg-slate-50'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-brand-600' : 'text-textSecondary'}`} />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>
        </div>

        <div className="text-xs text-textSecondary border-t border-border pt-4">
          <p className="font-semibold text-textPrimary">APATI ASPIS MVP</p>
          <p>Version 0.1.0 — Free Tier</p>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Mobile Top Header */}
        <header className="md:hidden bg-surface border-b border-border p-4 flex items-center justify-between sticky top-0 z-10 shadow-sm">
          <Logo size="sm" />
        </header>

        {/* Mobile Bottom Tab Bar */}
        <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-surface border-t border-border z-20 flex justify-around py-2 px-1 shadow-lg">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeRoute === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onNavigate(item.id)}
                className={`flex flex-col items-center py-1 px-2 text-[10px] font-medium transition-colors ${
                  isActive ? 'text-brand-600 font-bold' : 'text-textSecondary'
                }`}
              >
                <Icon className="w-5 h-5 mb-0.5" />
                <span>{item.label.split(' ')[0]}</span>
              </button>
            )}
          )}
        </nav>

        {/* Content Body */}
        <main className="flex-1 max-w-5xl w-full mx-auto p-4 md:p-8 pb-24 md:pb-8">
          {children}
        </main>

        <DisclaimerFooter />
      </div>
    </div>
  );
};
