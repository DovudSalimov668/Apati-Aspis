import React from 'react';

export const DisclaimerFooter: React.FC = () => {
  return (
    <footer className="w-full border-t border-border bg-surface py-6 px-4 text-center text-xs text-textSecondary mt-auto">
      <div className="max-w-4xl mx-auto space-y-1">
        <p className="font-medium text-textPrimary">APATI ASPIS — Digital Safety Platform</p>
        <p className="opacity-80">
          Provides risk analysis and educational guidance. It does not guarantee that an indicator is completely safe or malicious and should not replace professional enterprise security analysis.
        </p>
      </div>
    </footer>
  );
};
