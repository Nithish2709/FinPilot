import React from 'react';
import { Search, Bell, Settings, Menu, Terminal } from 'lucide-react';

interface HeaderProps {
  onToggleMobileMenu: () => void;
  onOpenPromptModal: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  onToggleMobileMenu,
  onOpenPromptModal
}) => {
  return (
    <header className="fixed top-0 left-0 lg:left-64 right-0 h-16 bg-[#0c0e13]/85 backdrop-blur-xl z-30 px-4 md:px-6 flex items-center justify-between border-b border-white/5">
      <div className="flex items-center gap-3 md:gap-4 flex-1">
        {/* Mobile Menu Button */}
        <button
          onClick={onToggleMobileMenu}
          className="p-2 rounded-lg text-[#b9cacb] hover:text-[#dbfcff] hover:bg-[#1d2025] lg:hidden transition-colors"
          aria-label="Toggle Navigation"
        >
          <Menu className="w-5 h-5" />
        </button>

        {/* Global Search Bar */}
        <div className="relative flex items-center w-full max-w-xs md:max-w-md">
          <Search className="absolute left-3 w-4 h-4 text-[#849495]" />
          <input
            type="text"
            placeholder="Search financial memory, transactions, scenarios..."
            className="w-full bg-[#191c21]/90 hover:bg-[#1d2025] text-[#e2e2ea] placeholder:text-[#849495] text-xs rounded-xl pl-9 pr-4 py-2 border border-white/5 focus:border-[#00dbe9]/50 focus:ring-1 focus:ring-[#00dbe9]/50 focus:outline-none transition-all"
          />
        </div>

        {/* Telemetry Status Badges (Tablet/Desktop) */}
        <div className="hidden xl:flex items-center gap-2">
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-[#191c21]/80 border border-white/5">
            <span className="font-['JetBrains_Mono'] text-[10px] text-[#849495] uppercase font-semibold">RUNWAY</span>
            <span className="font-['JetBrains_Mono'] text-xs text-[#00e296] font-semibold">4.8 MO</span>
          </div>

          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-[#191c21]/80 border border-white/5">
            <span className="font-['JetBrains_Mono'] text-[10px] text-[#849495] uppercase font-semibold">COMMITTED</span>
            <span className="font-['JetBrains_Mono'] text-xs text-[#b0c6ff] font-semibold">34%</span>
          </div>

          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-[#191c21]/80 border border-white/5">
            <span className="h-1.5 w-1.5 rounded-full bg-[#00dbe9] shadow-[0_0_6px_#00dbe9]"></span>
            <span className="font-['JetBrains_Mono'] text-[10px] text-[#00dbe9] font-semibold uppercase tracking-wider">
              CORE CONFIDENCE 99.8%
            </span>
          </div>
        </div>
      </div>

      {/* Right Action Icons & Avatar */}
      <div className="flex items-center gap-2 md:gap-3">
        {/* Antigravity Prompt Button */}
        <button
          onClick={onOpenPromptModal}
          className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#00f0ff]/10 hover:bg-[#00f0ff]/20 text-[#00f0ff] border border-[#00f0ff]/40 text-xs font-semibold font-['JetBrains_Mono'] transition-all shadow-[0_0_15px_-4px_rgba(0,240,255,0.3)]"
          title="Get Antigravity Prompt"
        >
          <Terminal className="w-3.5 h-3.5" />
          <span>Antigravity Prompt</span>
        </button>

        <button 
          className="p-2 rounded-lg text-[#b9cacb] hover:text-[#e2e2ea] hover:bg-[#1d2025] transition-colors relative"
          aria-label="Notifications"
        >
          <Bell className="w-4 h-4" />
          <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 rounded-full bg-[#00f0ff]"></span>
        </button>

        <button 
          className="p-2 rounded-lg text-[#b9cacb] hover:text-[#e2e2ea] hover:bg-[#1d2025] transition-colors"
          aria-label="Settings"
        >
          <Settings className="w-4 h-4" />
        </button>

        {/* User Profile */}
        <div className="relative flex items-center pl-1 cursor-pointer group">
          <div className="relative">
            <div className="w-8 h-8 rounded-full overflow-hidden ring-1 ring-[#00f0ff]/40 bg-[#1d2025]">
              <img
                src="https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=150&q=80"
                alt="Vikram Advisor"
                className="w-full h-full object-cover"
              />
            </div>
            <span className="absolute bottom-0 right-0 w-2 h-2 rounded-full bg-[#00e296] ring-2 ring-[#0c0e13]"></span>
          </div>
        </div>
      </div>
    </header>
  );
};
