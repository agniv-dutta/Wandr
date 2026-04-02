import React from 'react';

interface TabBarProps {
  tabs: Array<{ id: string; label: string }>;
  activeTab: string;
  onChange: (tabId: string) => void;
  className?: string;
}

export const TabBar: React.FC<TabBarProps> = ({ tabs, activeTab, onChange, className = '' }) => {
  return (
    <div className={`flex gap-1 border-b border-zinc-700 overflow-x-auto ${className}`}>
      {tabs.map(tab => (
        <button
          key={tab.id}
          onClick={() => onChange(tab.id)}
          className={`px-4 py-3 font-medium text-sm transition-all duration-300 whitespace-nowrap ${
            activeTab === tab.id
              ? 'text-violet-400 border-b-2 border-violet-500'
              : 'text-zinc-500 hover:text-zinc-300 border-b-2 border-transparent'
          }`}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
};
