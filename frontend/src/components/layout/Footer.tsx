import React from 'react';

export const Footer: React.FC = () => {
  return (
    <footer className="bg-zinc-950 border-t border-zinc-800 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col items-center justify-center text-center gap-4">
          <div className="flex items-center gap-2">
            <span className="text-2xl">✈</span>
            <span className="text-xl font-bold bg-gradient-to-r from-violet-400 to-indigo-400 bg-clip-text text-transparent">
              Wandr
            </span>
          </div>
          <p className="text-zinc-400 text-sm">
            AI-Powered Travel Planning
          </p>
          <p className="text-zinc-500 text-xs">
            Built with LangChain, Groq, and React
          </p>
          <p className="text-zinc-600 text-xs">
            Lab CA 1 | Sem VI | 2026
          </p>
        </div>
      </div>
    </footer>
  );
};
