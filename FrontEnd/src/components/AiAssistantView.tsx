import React, { useState, useEffect, useRef } from 'react';
import { 
  Sparkles, 
  Bot, 
  User, 
  PieChart, 
  Calendar, 
  Lock, 
  Laptop, 
  ArrowRightLeft, 
  ShieldCheck, 
  AlertTriangle, 
  CheckCircle2, 
  XCircle, 
  TrendingDown, 
  Sliders, 
  ThumbsUp, 
  ThumbsDown, 
  Copy, 
  Bookmark, 
  Paperclip, 
  Mic, 
  ArrowUp, 
  X, 
  Building, 
  CreditCard, 
  Clock,
  Loader2,
  FileText
} from 'lucide-react';
import { chatApi } from '../api/chat';
import { dashboardApi } from '../api/dashboard';
import { documentsApi } from '../api/documents';
import { purchasesApi } from '../api/purchases';
import { useAuth } from '../context/AuthContext';
import { Message, DashboardResponse, PurchaseAnalysisResponse } from '../types';

interface AiAssistantViewProps {
  onNavigateToScenario: () => void;
  initialQuery?: string;
  conversationId?: string;
  onConversationCreated?: (id: string) => void;
}

export const AiAssistantView: React.FC<AiAssistantViewProps> = ({
  onNavigateToScenario,
  initialQuery,
  conversationId,
  onConversationCreated
}) => {
  const { isAuthenticated } = useAuth();
  const [currentConvId, setCurrentConvId] = useState<string | undefined>(conversationId);
  const [messages, setMessages] = useState<Message[]>([]);
  const [userPrompt, setUserPrompt] = useState<string>(initialQuery || '');
  const [loading, setLoading] = useState<boolean>(false);
  const [dashboardData, setDashboardData] = useState<DashboardResponse | null>(null);
  const [attachedFile, setAttachedFile] = useState<File | null>(null);
  const [uploadingDoc, setUploadingDoc] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  // Dynamic interactive slider state
  const [sliderAmount, setSliderAmount] = useState<number>(50000);
  const [analysisResult, setAnalysisResult] = useState<PurchaseAnalysisResponse | null>(null);
  const [analyzingSlider, setAnalyzingSlider] = useState<boolean>(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Sync prop changes
  useEffect(() => {
    if (conversationId !== currentConvId) {
      setCurrentConvId(conversationId);
    }
  }, [conversationId]);

  useEffect(() => {
    if (initialQuery) {
      setUserPrompt(initialQuery);
    }
  }, [initialQuery]);

  // Load baseline dashboard metrics from backend
  useEffect(() => {
    if (isAuthenticated) {
      dashboardApi.getDashboard().then(setDashboardData).catch(() => {});
    }
  }, [isAuthenticated]);

  // Load conversation messages whenever active conversation changes
  useEffect(() => {
    if (isAuthenticated && currentConvId) {
      setLoading(true);
      chatApi.getMessages(currentConvId)
        .then((res: any) => {
          if (Array.isArray(res)) {
            setMessages(res);
          } else if (res && Array.isArray(res.items)) {
            setMessages(res.items);
          } else {
            setMessages([]);
          }
        })
        .catch(() => setMessages([]))
        .finally(() => setLoading(false));
    } else {
      setMessages([]);
    }
  }, [isAuthenticated, currentConvId]);

  // Scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  // Live slider backend calculation debounce
  useEffect(() => {
    if (!isAuthenticated || sliderAmount <= 0) return;
    const timer = setTimeout(() => {
      setAnalyzingSlider(true);
      purchasesApi.analyzePurchase({
        amount: sliderAmount,
        category: 'Electronics',
        description: 'Interactive AI Assistant Simulator'
      })
        .then(setAnalysisResult)
        .catch(() => setAnalysisResult(null))
        .finally(() => setAnalyzingSlider(false));
    }, 400);

    return () => clearTimeout(timer);
  }, [sliderAmount, isAuthenticated]);

  const handleSendMessage = async (textToSend?: string) => {
    const prompt = (textToSend || userPrompt).trim();
    if (!prompt) return;

    if (!isAuthenticated) {
      alert('Please log in with the demo account (admin@finpilot.ai) to use the AI Assistant.');
      return;
    }

    try {
      setLoading(true);
      setUserPrompt('');

      let activeConvId = currentConvId;
      if (!activeConvId) {
        const newConv = await chatApi.createConversation(prompt.slice(0, 40) + '...');
        activeConvId = newConv.id;
        setCurrentConvId(activeConvId);
        onConversationCreated?.(activeConvId);
      }

      // Optimistic user message append
      const optimisticMsg: Message = {
        id: 'temp-' + Date.now(),
        conversation_id: activeConvId,
        sender: 'user',
        content: prompt,
        created_at: new Date().toISOString()
      };
      setMessages((prev) => [...prev, optimisticMsg]);

      // Server dispatch
      const aiReply = await chatApi.sendMessage(activeConvId, prompt);
      setMessages((prev) => [...prev.filter((m) => m.id !== optimisticMsg.id), optimisticMsg, aiReply]);
    } catch (err: any) {
      alert(err.message || 'Failed to get response from FinPilot Neural Engine');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || !e.target.files[0]) return;
    const file = e.target.files[0];
    setAttachedFile(file);

    if (isAuthenticated) {
      setUploadingDoc(true);
      try {
        await documentsApi.uploadDocument(file);
        setUserPrompt(`I uploaded ${file.name}. Can you analyze its impact on my cashflow?`);
      } catch (err: any) {
        alert('File upload failed: ' + (err.message || 'Unknown error'));
      } finally {
        setUploadingDoc(false);
      }
    }
  };

  const handleCopyMessage = (msgId: string, content: string) => {
    navigator.clipboard.writeText(content);
    setCopiedId(msgId);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="flex flex-col gap-6 w-full max-w-7xl mx-auto pb-32 relative">
      {/* Dynamic Ambient Glow Backdrop */}
      <div className="absolute -top-12 left-1/2 -translate-x-1/2 w-3/4 h-64 bg-[#0068ed]/10 rounded-full blur-3xl pointer-events-none -z-10" />
      <div className="absolute top-48 right-10 w-96 h-96 bg-[#00f0ff]/5 rounded-full blur-3xl pointer-events-none -z-10" />

      {/* Atmospheric System Banner */}
      <section className="flex flex-col gap-4 pt-2">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-[#282a30]/80 backdrop-blur-md border border-white/5 shadow-sm">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#00dbe9] opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-[#7df4ff]"></span>
            </span>
            <span className="font-['JetBrains_Mono'] text-[11px] text-[#dbfcff] uppercase tracking-widest font-semibold">
              FINPILOT NEURAL AGENT
            </span>
            <span className="text-[#3b494b]">•</span>
            <span className="font-['JetBrains_Mono'] text-[11px] text-[#00e296] uppercase tracking-wider font-semibold">
              LIVE POSTGRESQL & PGVECTOR RETRIEVAL
            </span>
          </div>

          <div className="flex items-center gap-3 text-[#849495] font-['JetBrains_Mono'] text-xs">
            <span className="flex items-center gap-1 text-[#b9cacb]">
              <Lock className="w-3.5 h-3.5 text-[#00e296]" /> JWT BEARER
            </span>
            <span>•</span>
            <span className="flex items-center gap-1 text-[#b9cacb]">
              <Clock className="w-3.5 h-3.5 text-[#00dbe9]" /> CONVERSATION CACHE
            </span>
          </div>
        </div>

        {/* Main Welcome Title & Narrative */}
        <div className="flex flex-col gap-2 max-w-3xl">
          <h1 className="font-['Plus_Jakarta_Sans'] text-2xl md:text-4xl font-bold text-[#dbfcff] tracking-tight">
            FinPilot Decision Intelligence
          </h1>
          <p className="text-sm md:text-base text-[#b9cacb] leading-relaxed">
            Query your verified bank statements, simulate large expenses against upcoming obligations, or inspect subscription commitments. Evidence-based analysis calculated by the FastAPI financial engine.
          </p>
        </div>

        {/* Quick Telemetry Prompt Matrix (6 Cards) */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5 pt-1">
          {[
            {
              title: 'Where did my money go this month?',
              sub: 'Category breakdown & burn rate audit',
              icon: <PieChart className="w-4 h-4 text-[#00dbe9]" />
            },
            {
              title: 'Show me my recurring subscriptions',
              sub: 'Cadence detected recurring commitments',
              icon: <Calendar className="w-4 h-4 text-[#b0c6ff]" />
            },
            {
              title: 'How much of my budget is committed?',
              sub: 'Fixed obligations vs discretionary safety',
              icon: <Lock className="w-4 h-4 text-[#00e296]" />
            },
            {
              title: 'Can I afford a ₹50,000 laptop?',
              sub: 'Liquidity stress testing • 60-day safety buffer',
              icon: <Laptop className="w-4 h-4 text-[#7df4ff]" />
            },
            {
              title: 'What changed compared with last month?',
              sub: 'MoM expenditure variance & anomaly scan',
              icon: <ArrowRightLeft className="w-4 h-4 text-[#d9e2ff]" />
            },
            {
              title: 'How will this affect my emergency goal?',
              sub: 'Impact on active savings milestones',
              icon: <ShieldCheck className="w-4 h-4 text-[#4dffb1]" />
            }
          ].map((item, idx) => (
            <button
              key={idx}
              onClick={() => {
                setUserPrompt(item.title);
                handleSendMessage(item.title);
              }}
              className="flex items-start gap-3 p-3 rounded-xl bg-[#191c21]/90 hover:bg-[#282a30] border border-white/5 hover:border-[#00f0ff]/30 text-left transition-all group shadow-sm"
            >
              <span className="p-2 rounded-lg bg-[#1d2025] group-hover:scale-110 transition-transform shrink-0">
                {item.icon}
              </span>
              <div className="flex flex-col min-w-0">
                <span className="text-xs font-semibold text-[#e2e2ea] group-hover:text-[#dbfcff] transition-colors truncate">
                  {item.title}
                </span>
                <span className="font-['JetBrains_Mono'] text-[10px] text-[#849495] truncate mt-0.5">
                  {item.sub}
                </span>
              </div>
            </button>
          ))}
        </div>
      </section>

      {/* Live Financial Metrics Banner (Real Data from backend) */}
      {dashboardData && (
        <section className="grid grid-cols-2 sm:grid-cols-4 gap-3 p-3.5 rounded-xl bg-[#1d2025]/50 border border-white/5">
          <div>
            <span className="font-['JetBrains_Mono'] text-[10px] text-[#849495] uppercase">Total Balance</span>
            <p className="font-['JetBrains_Mono'] text-lg font-bold text-[#dbfcff]">
              ₹{dashboardData.total_balance?.toLocaleString('en-IN') || '0'}
            </p>
          </div>
          <div>
            <span className="font-['JetBrains_Mono'] text-[10px] text-[#849495] uppercase">Monthly Inflow</span>
            <p className="font-['JetBrains_Mono'] text-lg font-bold text-[#00e296]">
              +₹{dashboardData.monthly_income?.toLocaleString('en-IN') || '0'}
            </p>
          </div>
          <div>
            <span className="font-['JetBrains_Mono'] text-[10px] text-[#849495] uppercase">Monthly Outflow</span>
            <p className="font-['JetBrains_Mono'] text-lg font-bold text-[#ffb4ab]">
              -₹{dashboardData.monthly_expenses?.toLocaleString('en-IN') || '0'}
            </p>
          </div>
          <div>
            <span className="font-['JetBrains_Mono'] text-[10px] text-[#849495] uppercase">Safe To Spend</span>
            <p className="font-['JetBrains_Mono'] text-lg font-bold text-[#00dbe9]">
              ₹{dashboardData.safe_to_spend?.toLocaleString('en-IN') || '0'}
            </p>
          </div>
        </section>
      )}

      {/* Interactive Purchase Simulator Section */}
      <section className="p-4 rounded-xl bg-[#111319]/90 border border-white/5 flex flex-col gap-3">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <Sliders className="w-4 h-4 text-[#00f0ff]" />
            <span className="font-['Plus_Jakarta_Sans'] text-xs font-semibold text-[#e2e2ea]">
              Live Purchase Cost Stress-Tester (Backend Engine)
            </span>
          </div>
          <div className="flex items-center gap-2 font-['JetBrains_Mono'] text-sm">
            <span className="text-[#849495] text-xs">SIMULATED AMOUNT:</span>
            <span className="text-[#00f0ff] font-bold">
              ₹{sliderAmount.toLocaleString('en-IN')}
            </span>
            {analyzingSlider && <Loader2 className="w-3.5 h-3.5 text-[#00f0ff] animate-spin" />}
          </div>
        </div>

        <input
          type="range"
          min="5000"
          max="150000"
          step="5000"
          value={sliderAmount}
          onChange={(e) => setSliderAmount(parseInt(e.target.value, 10))}
          className="w-full h-2 bg-[#282a30] rounded-lg appearance-none cursor-pointer accent-[#00f0ff]"
        />

        {analysisResult && (
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 pt-1 font-['JetBrains_Mono']">
            <div className="p-2.5 rounded bg-[#1d2025]/50 border border-white/5 flex flex-col">
              <span className="text-[10px] text-[#849495] uppercase">Buffer After Purchase</span>
              <span className={`text-base font-bold ${analysisResult.buffer_after_purchase < 0 ? 'text-[#ffb4ab]' : 'text-[#00e296]'}`}>
                ₹{analysisResult.buffer_after_purchase?.toLocaleString('en-IN')}
              </span>
            </div>
            <div className="p-2.5 rounded bg-[#1d2025]/50 border border-white/5 flex flex-col">
              <span className="text-[10px] text-[#849495] uppercase">Recommendation</span>
              <span className={`text-base font-bold ${analysisResult.recommendation === 'BUY' ? 'text-[#00e296]' : analysisResult.recommendation === 'WAIT' ? 'text-[#f59e0b]' : 'text-[#ffb4ab]'}`}>
                {analysisResult.recommendation}
              </span>
            </div>
            <div className="p-2.5 rounded bg-[#1d2025]/50 border border-white/5 flex flex-col">
              <span className="text-[10px] text-[#849495] uppercase">Confidence</span>
              <span className="text-base font-bold text-[#dbfcff]">
                {(analysisResult.confidence_score * 100).toFixed(0)}%
              </span>
            </div>
          </div>
        )}
      </section>

      {/* Chat Dialogue Stream */}
      <section className="flex flex-col gap-4 pt-3">
        {messages.length === 0 && !loading && (
          <div className="p-8 rounded-2xl bg-[#191c21]/50 border border-dashed border-white/10 text-center flex flex-col items-center gap-2">
            <Bot className="w-10 h-10 text-[#00f0ff]/50" />
            <h3 className="font-['Plus_Jakarta_Sans'] font-semibold text-[#dbfcff]">
              Start a Financial Dialogue
            </h3>
            <p className="text-xs text-[#849495] max-w-md">
              Ask any question above or type your financial query below. FinPilot's multi-agent orchestrator will search documents and run scenarios.
            </p>
          </div>
        )}

        {Array.isArray(messages) && messages.map((msg) => {
          const isUser = msg.role === 'USER' || (msg as any).sender === 'user' || (msg as any).sender === 'USER';
          return (
            <div
              key={msg.id}
              className={`flex items-start gap-3 ${isUser ? 'justify-end' : 'justify-start'}`}
            >
              {!isUser && (
                <div className="w-9 h-9 rounded-full bg-[#1d2025] border border-[#00f0ff]/40 flex items-center justify-center text-[#00f0ff] shadow-[0_0_15px_-3px_rgba(0,240,255,0.4)] shrink-0">
                  <Bot className="w-5 h-5" />
                </div>
              )}

              <div className={`flex flex-col ${isUser ? 'items-end' : 'items-start'} max-w-2xl min-w-0`}>
                <div
                  className={`p-4 rounded-2xl ${
                    isUser
                      ? 'rounded-tr-none bg-[#282a30] border border-white/10 text-[#dbfcff]'
                      : 'rounded-tl-none bg-[#191c21]/90 backdrop-blur-2xl border border-[#00f0ff]/20 text-[#e2e2ea] shadow-xl'
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap leading-relaxed">{msg.content}</p>

                  {/* Metadata / Sources if available */}
                  {msg.metadata?.sources && msg.metadata.sources.length > 0 && (
                    <div className="mt-3 pt-2 border-t border-white/5 flex flex-col gap-1">
                      <span className="font-['JetBrains_Mono'] text-[10px] text-[#849495] uppercase">
                        Evidence Sources:
                      </span>
                      <div className="flex flex-wrap gap-1.5">
                        {msg.metadata.sources.map((src: any, i: number) => (
                          <span
                            key={i}
                            className="px-2 py-0.5 rounded bg-[#1d2025] text-[10px] font-['JetBrains_Mono'] text-[#00e296] flex items-center gap-1"
                          >
                            <FileText className="w-3 h-3" />
                            {src.name || src.document_id || 'Statement Chunk'}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                <div className="flex items-center gap-2 font-['JetBrains_Mono'] text-[10px] text-[#849495] mt-1 px-1">
                  <span>{isUser ? 'YOU' : 'FINPILOT AGENT'}</span>
                  <span>•</span>
                  <span>{new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                  {!isUser && (
                    <button
                      onClick={() => handleCopyMessage(msg.id, msg.content)}
                      className="ml-2 hover:text-[#00f0ff] transition-colors"
                      title="Copy response"
                    >
                      {copiedId === msg.id ? 'Copied!' : <Copy className="w-3 h-3" />}
                    </button>
                  )}
                </div>
              </div>

              {isUser && (
                <div className="w-8 h-8 rounded-full bg-[#0068ed] flex items-center justify-center text-white shadow-sm shrink-0">
                  <User className="w-4 h-4" />
                </div>
              )}
            </div>
          );
        })}

        {loading && (
          <div className="flex items-start gap-3">
            <div className="w-9 h-9 rounded-full bg-[#1d2025] border border-[#00f0ff]/40 flex items-center justify-center text-[#00f0ff] animate-pulse shrink-0">
              <Bot className="w-5 h-5" />
            </div>
            <div className="p-4 rounded-2xl rounded-tl-none bg-[#191c21]/90 border border-[#00f0ff]/20 text-[#e2e2ea] flex items-center gap-2">
              <Loader2 className="w-4 h-4 text-[#00f0ff] animate-spin" />
              <span className="text-xs font-['JetBrains_Mono'] text-[#b9cacb]">
                FinPilot is executing retrieval and financial stress-testing...
              </span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </section>

      {/* Persistent Bottom Chat Console */}
      <div className="fixed bottom-3 left-0 lg:left-64 right-0 px-4 md:px-6 z-20 pointer-events-none">
        <div className="max-w-7xl mx-auto p-3 rounded-2xl bg-[#191c21]/95 border border-[#00f0ff]/30 backdrop-blur-2xl shadow-2xl flex flex-col gap-2 pointer-events-auto">
          {/* Controls Bar */}
          <div className="flex items-center justify-between px-1">
            <div className="flex items-center gap-2">
              <label className="cursor-pointer flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-[#1d2025] hover:bg-[#282a30] text-[#b9cacb] hover:text-[#e2e2ea] font-['JetBrains_Mono'] text-[10px] transition-colors">
                <Paperclip className="w-3.5 h-3.5 text-[#00f0ff]" />
                <span>{uploadingDoc ? 'UPLOADING...' : 'ATTACH STATEMENT / CSV'}</span>
                <input
                  type="file"
                  accept=".pdf,.csv,.xlsx,.txt"
                  className="hidden"
                  disabled={uploadingDoc}
                  onChange={handleFileUpload}
                />
              </label>

              {attachedFile && (
                <div className="font-['JetBrains_Mono'] text-[11px] text-[#00e296] flex items-center gap-1">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>{attachedFile.name}</span>
                  <button onClick={() => setAttachedFile(null)} className="ml-1 text-[#849495] hover:text-[#ffb4ab]">
                    <X className="w-3 h-3" />
                  </button>
                </div>
              )}
            </div>

            <div className="hidden sm:flex items-center gap-1.5 text-[#849495] font-['JetBrains_Mono'] text-[10px]">
              <span className="h-1.5 w-1.5 rounded-full bg-[#00e296]"></span>
              <span>SYNAPSE ENGINE READY</span>
            </div>
          </div>

          {/* Main Input Textarea */}
          <div className="relative flex items-center">
            <textarea
              value={userPrompt}
              onChange={(e) => setUserPrompt(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSendMessage();
                }
              }}
              placeholder="Ask FinPilot anything about your finances, cashflow buffers, or purchase readiness..."
              rows={2}
              className="w-full bg-[#0c0e13]/80 text-[#e2e2ea] placeholder:text-[#849495] text-xs md:text-sm rounded-xl py-2 pl-3 pr-28 resize-none focus:outline-none focus:ring-1 focus:ring-[#00f0ff] transition-all border border-white/5"
            />

            <div className="absolute right-2 bottom-2 flex items-center gap-1.5">
              {userPrompt && (
                <button
                  onClick={() => setUserPrompt('')}
                  className="p-1.5 text-[#849495] hover:text-[#e2e2ea] transition-colors"
                  title="Clear input"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
              <button
                onClick={() => handleSendMessage()}
                disabled={loading || !userPrompt.trim()}
                className="px-3.5 py-1.5 rounded-lg bg-gradient-to-r from-[#0068ed] to-[#00f0ff] text-[#002d6e] hover:brightness-110 disabled:opacity-50 font-['Plus_Jakarta_Sans'] text-xs font-bold transition-all flex items-center gap-1 shadow-md"
              >
                <span>Analyze</span>
                <ArrowUp className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
