import React, { useState } from 'react';
import { Search, Bell, Settings, Menu, Terminal, LogIn, LogOut, User as UserIcon } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { AuthModal } from './AuthModal';

interface HeaderProps {
  onToggleMobileMenu: () => void;
  onOpenPromptModal: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  onToggleMobileMenu,
  onOpenPromptModal
}) => {
  const { user, isAuthenticated, logout } = useAuth();
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);

  return (
    <>
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
              <span className="font-['JetBrains_Mono'] text-[10px] text-[#849495] uppercase font-semibold">ENGINE</span>
              <span className="font-['JetBrains_Mono'] text-xs text-[#00e296] font-semibold">QWEN + API FALLBACK</span>
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
            <span>Prompt Spec</span>
          </button>

          {/* Auth Button or User Profile */}
          {isAuthenticated && user ? (
            <div className="flex items-center gap-2.5 pl-2 border-l border-white/10">
              <div className="flex flex-col text-right hidden md:flex">
                <span className="font-['Plus_Jakarta_Sans'] text-xs font-bold text-[#dbfcff]">
                  {user.name}
                </span>
                <span className="font-['JetBrains_Mono'] text-[10px] text-[#849495]">
                  {user.email}
                </span>
              </div>

              <div className="w-8 h-8 rounded-full bg-[#00f0ff]/10 border border-[#00f0ff]/30 text-[#00f0ff] flex items-center justify-center font-bold text-xs">
                {user.name.charAt(0).toUpperCase()}
              </div>

              <button
                onClick={() => logout()}
                className="p-2 rounded-lg text-[#849495] hover:text-[#ffb4ab] hover:bg-[#93000a]/20 transition-colors"
                title="Sign out"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <button
              onClick={() => setIsAuthModalOpen(true)}
              className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-[#0068ed] hover:bg-[#0068ed]/80 text-[#f2f3ff] text-xs font-bold font-['Plus_Jakarta_Sans'] transition-all shadow-md cursor-pointer"
            >
              <LogIn className="w-3.5 h-3.5" />
              <span>Sign In / Register</span>
            </button>
          )}
        </div>
      </header>

      <AuthModal
        isOpen={isAuthModalOpen}
        onClose={() => setIsAuthModalOpen(false)}
      />
    </>
  );
};

