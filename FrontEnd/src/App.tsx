import React, { useState } from 'react';
import { ViewMode } from './types';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { CommandCenterView } from './components/CommandCenterView';
import { AiAssistantView } from './components/AiAssistantView';
import { ScenarioEngineView } from './components/ScenarioEngineView';
import { SubscriptionsView } from './components/SubscriptionsView';
import { BudgetsGoalsView } from './components/BudgetsGoalsView';
import { FinancialDocumentsView } from './components/FinancialDocumentsView';
import { PromptModal } from './components/PromptModal';

export default function App() {
  const [currentView, setCurrentView] = useState<ViewMode>('ai-assistant');
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isPromptModalOpen, setIsPromptModalOpen] = useState(false);
  const [assistantQuery, setAssistantQuery] = useState<string | undefined>(undefined);

  const handleNavigateToAssistant = (query?: string) => {
    setAssistantQuery(query);
    setCurrentView('ai-assistant');
  };

  const handleOpenNewChat = () => {
    setAssistantQuery('');
    setCurrentView('ai-assistant');
  };

  return (
    <div className="min-h-screen bg-[#0c0e13] text-[#e2e2ea] flex flex-col font-['Inter'] relative selection:bg-[#00f0ff] selection:text-[#00363a]">
      {/* Fixed Left Navigation Deck */}
      <Sidebar
        currentView={currentView}
        onSelectView={setCurrentView}
        onOpenNewChat={handleOpenNewChat}
        onOpenPromptModal={() => setIsPromptModalOpen(true)}
        isOpenMobile={isMobileMenuOpen}
        onCloseMobile={() => setIsMobileMenuOpen(false)}
      />

      {/* Fixed Top Header */}
      <Header
        onToggleMobileMenu={() => setIsMobileMenuOpen(prev => !prev)}
        onOpenPromptModal={() => setIsPromptModalOpen(true)}
      />

      {/* Main View Area */}
      <main className="flex-1 lg:pl-64 pt-20 px-4 md:px-8 transition-all duration-300">
        {currentView === 'command-center' && (
          <CommandCenterView
            onNavigateToScenario={() => setCurrentView('scenario-engine')}
            onNavigateToAssistant={handleNavigateToAssistant}
          />
        )}

        {currentView === 'ai-assistant' && (
          <AiAssistantView
            onNavigateToScenario={() => setCurrentView('scenario-engine')}
            initialQuery={assistantQuery}
          />
        )}

        {currentView === 'scenario-engine' && (
          <ScenarioEngineView />
        )}

        {currentView === 'subscriptions' && (
          <SubscriptionsView />
        )}

        {currentView === 'budgets-goals' && (
          <BudgetsGoalsView />
        )}

        {currentView === 'financial-documents' && (
          <FinancialDocumentsView />
        )}
      </main>

      {/* Antigravity Prompt Modal */}
      <PromptModal
        isOpen={isPromptModalOpen}
        onClose={() => setIsPromptModalOpen(false)}
      />
    </div>
  );
}
