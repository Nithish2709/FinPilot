import React, { useEffect, useState } from 'react';
import { 
  Bot, 
  LayoutGrid, 
  GitBranch, 
  Calendar, 
  PiggyBank, 
  FileText, 
  PlusCircle, 
  Radio,
  Terminal,
  ChevronRight,
  Sparkles,
  MessageSquare
} from 'lucide-react';
import { ViewMode, Conversation } from '../types';
import { chatApi } from '../api/chat';
import { useAuth } from '../context/AuthContext';

interface SidebarProps {
  currentView: ViewMode;
  onSelectView: (view: ViewMode) => void;
  onOpenNewChat: () => void;
  onSelectConversation?: (conversationId: string) => void;
  selectedConversationId?: string;
  onOpenPromptModal: () => void;
  isOpenMobile: boolean;
  onCloseMobile: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentView,
  onSelectView,
  onOpenNewChat,
  onSelectConversation,
  selectedConversationId,
  onOpenPromptModal,
  isOpenMobile,
  onCloseMobile
}) => {
  const { isAuthenticated } = useAuth();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loadingConversations, setLoadingConversations] = useState(false);

  useEffect(() => {
    if (isAuthenticated) {
      setLoadingConversations(true);
      chatApi.getConversations(20)
        .then((res: any) => {
          if (Array.isArray(res)) {
            setConversations(res);
          } else if (res && Array.isArray(res.items)) {
            setConversations(res.items);
          } else {
            setConversations([]);
          }
        })
        .catch(() => {
          setConversations([]);
        })
        .finally(() => {
          setLoadingConversations(false);
        });
    } else {
      setConversations([]);
    }
  }, [isAuthenticated, selectedConversationId]);

  const navItems: { id: ViewMode; label: string; icon: React.ReactNode; colorClass: string }[] = [
    { 
      id: 'ai-assistant', 
      label: 'AI Assistant', 
      icon: <Bot className="w-4 h-4 text-[#00dbe9]" />, 
      colorClass: 'text-[#00dbe9]' 
    },
    { 
      id: 'command-center', 
      label: 'Command Center', 
      icon: <LayoutGrid className="w-4 h-4 text-[#b0c6ff]" />, 
      colorClass: 'text-[#b0c6ff]' 
    },
    { 
      id: 'scenario-engine', 
      label: 'Scenario Engine (Buy/Wait)', 
      icon: <GitBranch className="w-4 h-4 text-[#4dffb1]" />, 
      colorClass: 'text-[#4dffb1]' 
    },
    { 
      id: 'subscriptions', 
      label: 'Subscriptions & Commitments', 
      icon: <Calendar className="w-4 h-4 text-[#7df4ff]" />, 
      colorClass: 'text-[#7df4ff]' 
    },
    { 
      id: 'budgets-goals', 
      label: 'Budgets & Goals', 
      icon: <PiggyBank className="w-4 h-4 text-[#d9e2ff]" />, 
      colorClass: 'text-[#d9e2ff]' 
    },
    { 
      id: 'financial-documents', 
      label: 'Financial Documents', 
      icon: <FileText className="w-4 h-4 text-[#849495]" />, 
      colorClass: 'text-[#849495]' 
    }
  ];

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpenMobile && (
        <div 
          className="fixed inset-0 bg-black/70 backdrop-blur-sm z-40 lg:hidden"
          onClick={onCloseMobile}
        />
      )}

      <aside className={`
        fixed left-0 top-0 h-screen w-64 bg-[#0c0e13]/95 backdrop-blur-2xl z-50 flex flex-col justify-between 
        border-r border-white/5 transition-transform duration-300 ease-in-out
        ${isOpenMobile ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
        <div className="p-4 flex flex-col gap-4 overflow-y-auto">
          {/* Logo Header */}
          <div className="flex items-center gap-3 px-1">
            <div className="relative w-9 h-9 rounded-full bg-[#111319] border border-[#00f0ff]/40 flex items-center justify-center shadow-[0_0_15px_-3px_rgba(0,240,255,0.4)] shrink-0">
              <svg viewBox="0 0 40 40" className="w-6 h-6">
                <circle cx="20" cy="20" r="18" fill="none" stroke="#00363a" strokeWidth="1.5" strokeDasharray="3 3" />
                <path d="M20 7 L31 29 L20 23 L9 29 Z" fill="none" stroke="#00f0ff" strokeWidth="2.5" strokeLinejoin="round" />
                <line x1="20" y1="12" x2="20" y2="20" stroke="#00e296" strokeWidth="2" strokeLinecap="round" />
                <circle cx="20" cy="20" r="2.5" fill="#00f0ff" />
              </svg>
            </div>
            <div className="flex flex-col">
              <span className="font-['Plus_Jakarta_Sans'] font-bold text-lg text-[#dbfcff] tracking-tight leading-tight flex items-center gap-1.5">
                FinPilot
              </span>
              <span className="font-['JetBrains_Mono'] text-[10px] text-[#00dbe9] uppercase tracking-wider font-semibold">
                AI DECISION ENGINE
              </span>
            </div>
          </div>

          {/* New Chat Action Button */}
          <button 
            onClick={() => {
              onOpenNewChat();
              if (window.innerWidth < 1024) onCloseMobile();
            }}
            className="w-full py-2 px-3 rounded-xl bg-[#1d2025]/80 hover:bg-[#282a30] text-[#dbfcff] hover:text-[#7df4ff] border border-white/5 hover:border-[#00dbe9]/30 flex items-center justify-center gap-2 shadow-[0_0_20px_-5px_rgba(0,219,233,0.2)] transition-all group"
          >
            <PlusCircle className="w-4 h-4 text-[#00dbe9] group-hover:scale-110 transition-transform" />
            <span className="font-['Plus_Jakarta_Sans'] text-xs font-semibold tracking-wide">
              + New Analysis / Chat
            </span>
          </button>

          {/* Workspace Matrix Navigation */}
          <div className="flex flex-col gap-1 pt-1">
            <span className="font-['JetBrains_Mono'] text-[10px] text-[#849495] uppercase px-1 tracking-wider font-semibold">
              Workspace Matrix
            </span>
            <nav className="flex flex-col gap-0.5">
              {navItems.map((item) => {
                const isActive = currentView === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => {
                      onSelectView(item.id);
                      if (window.innerWidth < 1024) onCloseMobile();
                    }}
                    className={`
                      flex items-center gap-2.5 px-2.5 py-1.5 rounded-lg text-left transition-all text-xs font-medium
                      ${isActive 
                        ? 'bg-[#282a30] text-[#7df4ff] font-semibold border-l-2 border-[#00f0ff] shadow-inner' 
                        : 'text-[#b9cacb] hover:bg-[#1d2025] hover:text-[#e2e2ea]'
                      }
                    `}
                  >
                    <span className="shrink-0">{item.icon}</span>
                    <span className="truncate">{item.label}</span>
                  </button>
                );
              })}
            </nav>
          </div>

          {/* Dynamic Neural Memory / Conversation History */}
          <div className="flex flex-col gap-2 pt-2">
            <span className="font-['JetBrains_Mono'] text-[10px] text-[#849495] uppercase px-1 tracking-wider font-semibold flex items-center justify-between">
              <span>Neural Memory</span>
              <span className="text-[9px] text-[#00dbe9] font-normal">
                {loadingConversations ? 'Syncing...' : `${conversations?.length || 0} Active`}
              </span>
            </span>

            {(!Array.isArray(conversations) || conversations.length === 0) ? (
              <div className="px-2 py-3 text-center border border-dashed border-white/5 rounded-lg">
                <p className="text-[11px] text-[#849495]">
                  {isAuthenticated ? 'No prior analyses. Start a chat!' : 'Sign in to sync neural memory'}
                </p>
              </div>
            ) : (
              <div className="flex flex-col gap-1 max-h-48 overflow-y-auto">
                {conversations.map((conv) => {
                  const isSelected = selectedConversationId === conv.id;
                  return (
                    <button
                      key={conv.id}
                      onClick={() => {
                        if (onSelectConversation) {
                          onSelectConversation(conv.id);
                        } else {
                          onSelectView('ai-assistant');
                        }
                        if (window.innerWidth < 1024) onCloseMobile();
                      }}
                      className={`
                        flex items-center gap-2 px-2 py-1.5 rounded text-left text-xs transition-colors
                        ${isSelected 
                          ? 'bg-[#282a30] text-[#7df4ff] font-medium' 
                          : 'text-[#b9cacb] hover:bg-[#1d2025] hover:text-[#dbfcff]'
                        }
                      `}
                    >
                      <MessageSquare className="w-3 h-3 shrink-0 text-[#00dbe9]" />
                      <span className="truncate">{conv.title || 'Analysis Session'}</span>
                    </button>
                  );
                })}
              </div>
            )}
          </div>

          {/* Antigravity Prompt Trigger Pill */}
          <div className="pt-2">
            <button
              onClick={onOpenPromptModal}
              className="w-full p-2.5 rounded-xl bg-gradient-to-r from-[#0068ed]/20 to-[#00f0ff]/10 border border-[#00f0ff]/30 hover:border-[#00f0ff]/60 text-left transition-all group shadow-sm"
            >
              <div className="flex items-center justify-between text-xs">
                <span className="font-['JetBrains_Mono'] text-[10px] text-[#00f0ff] uppercase tracking-wider font-semibold flex items-center gap-1.5">
                  <Terminal className="w-3 h-3 text-[#00f0ff]" />
                  Antigravity Prompt
                </span>
                <ChevronRight className="w-3 h-3 text-[#00f0ff] group-hover:translate-x-0.5 transition-transform" />
              </div>
              <p className="text-[11px] text-[#b9cacb] mt-1 line-clamp-2">
                Get full production prompt for Antigravity AI builder.
              </p>
            </button>
          </div>
        </div>

        {/* Bottom Engine Telemetry Status */}
        <div className="p-3 bg-[#191c21]/60 border-t border-white/5">
          <div className="flex items-center justify-between p-2 rounded-lg bg-[#1d2025]/50 border border-white/5">
            <div className="flex items-center gap-2">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#00e296] opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-[#00e296]"></span>
              </span>
              <span className="font-['JetBrains_Mono'] text-[10px] text-[#b9cacb] font-medium tracking-wider">
                SYNAPSE V4.2
              </span>
            </div>
            <span className="font-['JetBrains_Mono'] text-[10px] text-[#00e296] font-semibold tracking-wider">
              ONLINE
            </span>
          </div>
        </div>
      </aside>
    </>
  );
};
