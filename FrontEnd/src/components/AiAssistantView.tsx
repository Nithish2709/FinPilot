import React, { useState } from 'react';
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
  TrendingUp, 
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
  RotateCw,
  Clock
} from 'lucide-react';

interface AiAssistantViewProps {
  onNavigateToScenario: () => void;
  initialQuery?: string;
}

export const AiAssistantView: React.FC<AiAssistantViewProps> = ({
  onNavigateToScenario,
  initialQuery
}) => {
  const [sliderAmount, setSliderAmount] = useState<number>(60000);
  const [userPrompt, setUserPrompt] = useState<string>(initialQuery || '');
  const [attachedFile, setAttachedFile] = useState<string | null>(null);
  const [actionLocked, setActionLocked] = useState<boolean>(false);
  const [copied, setCopied] = useState<boolean>(false);

  // Financial baseline numbers
  const totalLiquid = 85000;
  const obligations = 22000;
  const nextSalary = 90000;

  // Real-time calculations based on slider
  const immediateBuffer = totalLiquid - obligations - sliderAmount;
  const septBuffer = (totalLiquid - obligations - sliderAmount) + nextSalary;
  const bufferRatio = ((immediateBuffer / totalLiquid) * 100).toFixed(1);

  const getSafetyStatus = () => {
    if (immediateBuffer < 0) return { text: 'DEFICIT (Overdrawn)', color: 'text-[#ffb4ab]' };
    if (immediateBuffer < 10000) return { text: `${bufferRatio}% (Severe Deficit)`, color: 'text-[#ffb4ab]' };
    if (immediateBuffer < 25000) return { text: `${bufferRatio}% (Moderate Risk)`, color: 'text-[#b0c6ff]' };
    return { text: `${bufferRatio}% (Safe Range)`, color: 'text-[#00e296]' };
  };

  const safety = getSafetyStatus();

  const handleQuickPrompt = (promptText: string) => {
    setUserPrompt(promptText);
  };

  const handleCopyRationale = () => {
    navigator.clipboard.writeText(
      `FinPilot Scenario Analysis: Proposed ₹${sliderAmount.toLocaleString('en-IN')} CapEx.\nImmediate Buffer: ₹${immediateBuffer.toLocaleString('en-IN')}.\nPost-Salary Sept 1 Buffer: ₹${septBuffer.toLocaleString('en-IN')}.\nRecommendation: Purchase on Sept 1st post-payroll to maintain zero emergency liquidity friction.`
    );
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  return (
    <div className="flex flex-col gap-6 w-full max-w-7xl mx-auto pb-28 relative">
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
              FINPILOT NEURAL ENGINE v3.4
            </span>
            <span className="text-[#3b494b]">•</span>
            <span className="font-['JetBrains_Mono'] text-[11px] text-[#00e296] uppercase tracking-wider font-semibold">
              SYNCED TO REAL-TIME LEDGER
            </span>
          </div>

          <div className="flex items-center gap-3 text-[#849495] font-['JetBrains_Mono'] text-xs">
            <span className="flex items-center gap-1 text-[#b9cacb]">
              <Lock className="w-3.5 h-3.5 text-[#00e296]" /> AES-256 E2E
            </span>
            <span>•</span>
            <span className="flex items-center gap-1 text-[#b9cacb]">
              <Clock className="w-3.5 h-3.5 text-[#00dbe9]" /> 120-DAY CONTEXT CACHE
            </span>
          </div>
        </div>

        {/* Main Welcome Title & Narrative */}
        <div className="flex flex-col gap-2 max-w-3xl">
          <h1 className="font-['Plus_Jakarta_Sans'] text-2xl md:text-4xl font-bold text-[#dbfcff] tracking-tight">
            Good morning. I'm FinPilot — your financial decision engine.
          </h1>
          <p className="text-sm md:text-base text-[#b9cacb] leading-relaxed">
            Upload your financial statements or query spending trajectories, committed cashflows, buffer thresholds, and high-impact purchase scenarios. Evidence-based analysis, zero judgment.
          </p>
        </div>

        {/* Quick Telemetry Prompt Matrix (6 Cards) */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5 pt-1">
          {[
            {
              title: 'Where did my money go this month?',
              sub: 'Category delta + anomaly scan',
              icon: <PieChart className="w-4 h-4 text-[#00dbe9]" />
            },
            {
              title: 'Show me my recurring payments',
              sub: '14 subscriptions active • ₹22,000',
              icon: <Calendar className="w-4 h-4 text-[#b0c6ff]" />
            },
            {
              title: 'How much of my budget is committed?',
              sub: 'Fixed vs discretionary ratio: 34%',
              icon: <Lock className="w-4 h-4 text-[#00e296]" />
            },
            {
              title: 'Can I afford a ₹60,000 laptop?',
              sub: 'Liquidity stress testing • 60-day buffer',
              icon: <Laptop className="w-4 h-4 text-[#7df4ff]" />
            },
            {
              title: 'What changed compared with last month?',
              sub: '+18.4% dining • ₹12,400 investment drift',
              icon: <ArrowRightLeft className="w-4 h-4 text-[#d9e2ff]" />
            },
            {
              title: 'How will this affect my emergency goal?',
              sub: 'Goal: ₹3,00,000 • Current 74%',
              icon: <ShieldCheck className="w-4 h-4 text-[#4dffb1]" />
            }
          ].map((item, idx) => (
            <button
              key={idx}
              onClick={() => handleQuickPrompt(item.title)}
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

      {/* Chat Dialogue Stream */}
      <section className="flex flex-col gap-6 pt-3">
        {/* User Query Bubble */}
        <div className="flex items-start justify-end gap-3">
          <div className="flex flex-col items-end gap-1 max-w-xl">
            <div className="p-3.5 rounded-2xl rounded-tr-none bg-[#282a30] border border-white/10 text-[#dbfcff] shadow-md">
              <p className="text-sm font-medium">Can I buy a ₹60,000 laptop?</p>
            </div>
            <div className="flex items-center gap-2 font-['JetBrains_Mono'] text-[10px] text-[#849495]">
              <span>AUDITED QUERY</span>
              <span>•</span>
              <span>10:42 AM</span>
            </div>
          </div>
          <div className="w-8 h-8 rounded-full bg-[#0068ed] flex items-center justify-center text-white shadow-sm shrink-0">
            <User className="w-4 h-4" />
          </div>
        </div>

        {/* FinPilot AI Core Response Streamer */}
        <div className="flex items-start gap-3">
          <div className="w-9 h-9 rounded-full bg-[#1d2025] border border-[#00f0ff]/40 flex items-center justify-center text-[#00f0ff] shadow-[0_0_15px_-3px_rgba(0,240,255,0.4)] shrink-0">
            <Bot className="w-5 h-5" />
          </div>

          <div className="flex flex-col gap-4 flex-1 min-w-0">
            {/* Response HUD Container */}
            <div className="flex flex-col gap-4 p-4 md:p-6 rounded-2xl bg-[#191c21]/90 backdrop-blur-2xl border border-[#00f0ff]/20 shadow-2xl">
              {/* Telemetry Header Badges */}
              <div className="flex flex-wrap items-center justify-between gap-2 pb-1 border-b border-white/5">
                <div className="flex items-center gap-1.5">
                  <span className="px-2 py-0.5 rounded bg-[#1d2025] font-['JetBrains_Mono'] text-[10px] text-[#00dbe9] font-bold tracking-wider uppercase">
                    SCENARIO ANALYSIS
                  </span>
                  <span className="px-2 py-0.5 rounded bg-[#1d2025] font-['JetBrains_Mono'] text-[10px] text-[#00e296] tracking-wider uppercase font-semibold">
                    EVIDENCE BASED
                  </span>
                  <span className="px-2 py-0.5 rounded bg-[#1d2025] font-['JetBrains_Mono'] text-[10px] text-[#849495] tracking-wider uppercase">
                    NOT FINANCIAL ADVICE
                  </span>
                </div>
                <span className="font-['JetBrains_Mono'] text-[10px] text-[#849495]">
                  EXECUTION TIME: 142MS
                </span>
              </div>

              {/* AI Narrative */}
              <div className="flex flex-col gap-1.5">
                <p className="text-sm md:text-base text-[#e2e2ea]">
                  Analyzing your cash flow, upcoming obligations, and safety buffer requirements across a{' '}
                  <span className="text-[#00f0ff] font-semibold">60-day predictive horizon</span>.
                </p>
                <p className="text-xs md:text-sm text-[#b9cacb] leading-relaxed">
                  While your current ledger indicates sufficient balance to complete this purchase immediately, doing so triggers a severe short-term liquidity compression in the remaining 4 days before payroll.
                </p>
              </div>

              {/* Embedded 4-Col Financial Snapshot Card */}
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 p-3.5 rounded-xl bg-[#282a30]/60 border border-white/5 backdrop-blur-md">
                <div className="flex flex-col">
                  <span className="font-['JetBrains_Mono'] text-[10px] text-[#849495] uppercase tracking-wider font-semibold">
                    Current Liquid Cash
                  </span>
                  <span className="font-['JetBrains_Mono'] text-xl md:text-2xl font-bold text-[#e2e2ea]">
                    ₹85,000
                  </span>
                  <span className="text-[11px] text-[#00e296] flex items-center gap-1 mt-0.5">
                    <CheckCircle2 className="w-3 h-3" /> High confidence
                  </span>
                </div>

                <div className="flex flex-col">
                  <span className="font-['JetBrains_Mono'] text-[10px] text-[#849495] uppercase tracking-wider font-semibold">
                    Committed Obligations
                  </span>
                  <span className="font-['JetBrains_Mono'] text-xl md:text-2xl font-bold text-[#b0c6ff]">
                    ₹22,000
                  </span>
                  <span className="text-[11px] text-[#849495] mt-0.5 truncate">
                    Rent, 2x EMIs, Broadband
                  </span>
                </div>

                <div className="flex flex-col">
                  <span className="font-['JetBrains_Mono'] text-[10px] text-[#849495] uppercase tracking-wider font-semibold">
                    Proposed Purchase
                  </span>
                  <span className="font-['JetBrains_Mono'] text-xl md:text-2xl font-bold text-[#00f0ff]">
                    ₹{sliderAmount.toLocaleString('en-IN')}
                  </span>
                  <span className="text-[11px] text-[#849495] mt-0.5">
                    Hardware CapEx request
                  </span>
                </div>

                <div className="flex flex-col">
                  <span className="font-['JetBrains_Mono'] text-[10px] text-[#ffb4ab] uppercase tracking-wider font-semibold">
                    Immediate Remaining Buffer
                  </span>
                  <span className={`font-['JetBrains_Mono'] text-xl md:text-2xl font-bold ${safety.color}`}>
                    {immediateBuffer < 0 ? `-₹${Math.abs(immediateBuffer).toLocaleString('en-IN')}` : `₹${immediateBuffer.toLocaleString('en-IN')}`}
                  </span>
                  <span className={`text-[11px] flex items-center gap-1 mt-0.5 font-medium ${safety.color}`}>
                    <AlertTriangle className="w-3 h-3" /> {safety.text}
                  </span>
                </div>
              </div>

              {/* 60-Day Cash Flow Depletion Model SVG */}
              <div className="p-3.5 rounded-xl bg-[#111319]/80 border border-white/5 flex flex-col gap-2">
                <div className="flex items-center justify-between text-xs font-['JetBrains_Mono']">
                  <span className="text-[#849495] uppercase">60-Day Cash Flow Depletion Model</span>
                  <span className="text-[#00f0ff] font-semibold">CRITICAL DIP: AUG 27 - AUG 31</span>
                </div>

                <div className="h-20 w-full relative">
                  <svg className="w-full h-full text-[#00f0ff]" preserveAspectRatio="none" viewBox="0 0 600 80">
                    <defs>
                      <linearGradient id="curveFill" x1="0" x2="0" y1="0" y2="1">
                        <stop offset="0%" stopColor="#00dbe9" stopOpacity="0.25" />
                        <stop offset="100%" stopColor="#00dbe9" stopOpacity="0.0" />
                      </linearGradient>
                      <linearGradient id="dangerZone" x1="0" x2="1" y1="0" y2="0">
                        <stop offset="35%" stopColor="#00dbe9" stopOpacity="0.8" />
                        <stop offset="42%" stopColor="#ffb4ab" stopOpacity="1" />
                        <stop offset="52%" stopColor="#ffb4ab" stopOpacity="1" />
                        <stop offset="55%" stopColor="#00e296" stopOpacity="0.9" />
                      </linearGradient>
                    </defs>

                    <line stroke="#33353b" strokeDasharray="4 4" strokeOpacity="0.4" x1="0" x2="600" y1="20" y2="20" />
                    <line stroke="#33353b" strokeDasharray="4 4" strokeOpacity="0.4" x1="0" x2="600" y1="50" y2="50" />
                    <line stroke="#ffb4ab" strokeDasharray="2 2" strokeOpacity="0.5" x1="0" x2="600" y1="70" y2="70" />

                    <path d="M 0,30 Q 120,32 200,35 T 250,72 L 310,72 Q 330,12 380,15 T 600,18 L 600,80 L 0,80 Z" fill="url(#curveFill)" />
                    <path d="M 0,30 Q 120,32 200,35 T 250,72 L 310,72 Q 330,12 380,15 T 600,18" fill="none" stroke="url(#dangerZone)" strokeWidth="2.5" />

                    <circle cx="280" cy="72" fill="#ffb4ab" r="4" className="animate-pulse" />
                    <circle cx="330" cy="14" fill="#00e296" r="4" />
                  </svg>
                </div>

                <div className="flex items-center justify-between text-[#849495] font-['JetBrains_Mono'] text-[10px]">
                  <span>Today (₹85k)</span>
                  <span className="text-[#ffb4ab] font-semibold">Vulnerable Period (₹3k Buffer)</span>
                  <span className="text-[#00e296] font-semibold">Aug 31 Salary Credit (+₹90k)</span>
                  <span>Day 60 (₹1,48k)</span>
                </div>
              </div>

              {/* Dual Visual Scenario Comparison Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Option A Card */}
                <div className="flex flex-col justify-between p-4 rounded-xl bg-[#1d2025]/60 hover:bg-[#1d2025] border border-white/5 transition-all shadow-md">
                  <div className="flex flex-col gap-3">
                    <div className="flex items-center justify-between">
                      <span className="font-['Plus_Jakarta_Sans'] text-sm font-bold text-[#e2e2ea]">
                        OPTION A: BUY TODAY
                      </span>
                      <span className="px-2 py-0.5 rounded bg-[#93000a]/50 text-[#ffb4ab] font-['JetBrains_Mono'] text-[10px] font-bold">
                        HIGH FRICTION
                      </span>
                    </div>

                    <div className="flex items-baseline gap-2">
                      <span className="font-['JetBrains_Mono'] text-2xl font-bold text-[#ffb4ab]">
                        {immediateBuffer < 0 ? `-₹${Math.abs(immediateBuffer).toLocaleString('en-IN')}` : `₹${immediateBuffer.toLocaleString('en-IN')}`}
                      </span>
                      <span className="font-['JetBrains_Mono'] text-[10px] text-[#849495] uppercase">
                        POST-TX BUFFER
                      </span>
                    </div>

                    <div className="w-full bg-[#0c0e13] h-2 rounded-full overflow-hidden">
                      <div className="bg-[#ffb4ab] h-full rounded-full transition-all" style={{ width: `${Math.max(5, Math.min(100, (immediateBuffer / totalLiquid) * 100))}%` }}></div>
                    </div>

                    <div className="flex flex-col gap-2 pt-1 text-xs text-[#b9cacb]">
                      <div className="flex items-start gap-2">
                        <XCircle className="w-3.5 h-3.5 text-[#ffb4ab] shrink-0 mt-0.5" />
                        <span>Leaves only 4 days of coverage before the next regular salary credit.</span>
                      </div>
                      <div className="flex items-start gap-2">
                        <TrendingDown className="w-3.5 h-3.5 text-[#ffb4ab] shrink-0 mt-0.5" />
                        <span>Emergency liquidity falls to critical 12% boundary. Zero unexpected expense resilience.</span>
                      </div>
                      <div className="flex items-start gap-2">
                        <AlertTriangle className="w-3.5 h-3.5 text-[#849495] shrink-0 mt-0.5" />
                        <span>Mandates postponing your ₹5,000 discretionary weekend dining allocation.</span>
                      </div>
                    </div>
                  </div>

                  <div className="pt-4">
                    <button 
                      onClick={onNavigateToScenario}
                      className="w-full py-2 px-3 rounded-lg bg-[#282a30] hover:bg-[#33353b] text-[#e2e2ea] text-xs font-['JetBrains_Mono'] font-medium transition-colors flex items-center justify-center gap-1.5"
                    >
                      <span>Simulate Option A Consequences</span>
                      <span className="text-[#00f0ff]">→</span>
                    </button>
                  </div>
                </div>

                {/* Option B Card (AI Preferred) */}
                <div className="flex flex-col justify-between p-4 rounded-xl bg-[#282a30]/80 border border-[#00e296]/30 shadow-xl relative overflow-hidden">
                  <div className="flex flex-col gap-3">
                    <div className="flex items-center justify-between">
                      <span className="font-['Plus_Jakarta_Sans'] text-sm font-bold text-[#00f0ff]">
                        OPTION B: PURCHASE ON SEPT 1ST
                      </span>
                      <span className="px-2 py-0.5 rounded bg-[#00e296]/20 text-[#00e296] font-['JetBrains_Mono'] text-[10px] font-bold">
                        RECOMMENDED
                      </span>
                    </div>

                    <div className="flex items-baseline gap-2">
                      <span className="font-['JetBrains_Mono'] text-2xl font-bold text-[#00e296]">
                        ₹{septBuffer.toLocaleString('en-IN')}
                      </span>
                      <span className="font-['JetBrains_Mono'] text-[10px] text-[#849495] uppercase">
                        POST-TX BUFFER
                      </span>
                    </div>

                    <div className="w-full bg-[#0c0e13] h-2 rounded-full overflow-hidden">
                      <div className="bg-[#00e296] h-full rounded-full transition-all" style={{ width: '78%' }}></div>
                    </div>

                    <div className="flex flex-col gap-2 pt-1 text-xs text-[#b9cacb]">
                      <div className="flex items-start gap-2">
                        <CheckCircle2 className="w-3.5 h-3.5 text-[#00e296] shrink-0 mt-0.5" />
                        <span>Incoming recurring salary (+₹90,000) arrives Aug 31 with zero friction.</span>
                      </div>
                      <div className="flex items-start gap-2">
                        <ShieldCheck className="w-3.5 h-3.5 text-[#00e296] shrink-0 mt-0.5" />
                        <span>Zero disruption to ongoing ₹15,000 emergency fund SIP or recurring bills.</span>
                      </div>
                      <div className="flex items-start gap-2">
                        <Sparkles className="w-3.5 h-3.5 text-[#00f0ff] shrink-0 mt-0.5" />
                        <span>Evidence source: 8 consecutive months of verifiable on-time corporate credits.</span>
                      </div>
                    </div>
                  </div>

                  <div className="pt-4">
                    <button 
                      onClick={() => setActionLocked(true)}
                      className="w-full py-2 px-3 rounded-lg bg-gradient-to-r from-[#0068ed] to-[#00f0ff] text-[#002d6e] hover:brightness-110 text-xs font-['Plus_Jakarta_Sans'] font-bold transition-all flex items-center justify-center gap-1.5 shadow-[0_0_15px_rgba(0,240,255,0.4)]"
                    >
                      <Calendar className="w-3.5 h-3.5" />
                      <span>{actionLocked ? 'Calendar Alert Set for Sept 1 ✓' : 'Set Calendar Action for Sept 1'}</span>
                    </button>
                  </div>
                </div>
              </div>

              {/* Dynamic Interactive Purchase Cost Simulator */}
              <div className="p-4 rounded-xl bg-[#0c0e13]/80 border border-white/5 flex flex-col gap-3">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <Sliders className="w-4 h-4 text-[#00f0ff]" />
                    <span className="font-['Plus_Jakarta_Sans'] text-xs font-semibold text-[#e2e2ea]">
                      Interactive Purchase Cost Simulator
                    </span>
                  </div>
                  <div className="flex items-center gap-2 font-['JetBrains_Mono'] text-sm">
                    <span className="text-[#849495] text-xs">SIMULATED AMOUNT:</span>
                    <span className="text-[#00f0ff] font-bold">
                      ₹{sliderAmount.toLocaleString('en-IN')}
                    </span>
                  </div>
                </div>

                {/* Range Slider */}
                <div className="flex flex-col gap-1.5 py-1">
                  <input
                    type="range"
                    min="40000"
                    max="90000"
                    step="2500"
                    value={sliderAmount}
                    onChange={(e) => setSliderAmount(parseInt(e.target.value, 10))}
                    className="w-full h-2 bg-[#282a30] rounded-lg appearance-none cursor-pointer accent-[#00f0ff]"
                  />
                  <div className="flex justify-between font-['JetBrains_Mono'] text-[10px] text-[#849495]">
                    <span>₹40,000 (Budget Spec)</span>
                    <span>₹60,000 (Target Spec)</span>
                    <span>₹90,000 (Pro Workstation)</span>
                  </div>
                </div>

                {/* Dynamic Readouts Grid */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 pt-1 font-['JetBrains_Mono']">
                  <div className="p-2.5 rounded bg-[#1d2025]/50 border border-white/5 flex flex-col">
                    <span className="text-[10px] text-[#849495] uppercase">Simulated Immediate Buffer</span>
                    <span className={`text-base font-bold ${safety.color}`}>
                      {immediateBuffer < 0 ? `-₹${Math.abs(immediateBuffer).toLocaleString('en-IN')}` : `₹${immediateBuffer.toLocaleString('en-IN')}`}
                    </span>
                  </div>

                  <div className="p-2.5 rounded bg-[#1d2025]/50 border border-white/5 flex flex-col">
                    <span className="text-[10px] text-[#849495] uppercase">Simulated Sept 1st Buffer</span>
                    <span className="text-base font-bold text-[#00e296]">
                      ₹{septBuffer.toLocaleString('en-IN')}
                    </span>
                  </div>

                  <div className="p-2.5 rounded bg-[#1d2025]/50 border border-white/5 flex flex-col">
                    <span className="text-[10px] text-[#849495] uppercase">Safety Threshold Status</span>
                    <span className={`text-base font-bold ${safety.color}`}>
                      {safety.text}
                    </span>
                  </div>
                </div>
              </div>

              {/* Follow-up Quick Chips */}
              <div className="flex flex-wrap items-center gap-2 pt-1">
                <span className="font-['JetBrains_Mono'] text-[10px] text-[#849495] uppercase">
                  CONTINUE THREAD:
                </span>
                <button 
                  onClick={() => onNavigateToScenario()}
                  className="px-3 py-1 rounded-full bg-[#1d2025] hover:bg-[#282a30] text-xs text-[#b9cacb] hover:text-[#e2e2ea] border border-white/5 transition-colors"
                >
                  What if I split this into 3-month no-cost EMI?
                </button>
                <button 
                  onClick={() => setUserPrompt('Show my discretionary spending headroom this week')}
                  className="px-3 py-1 rounded-full bg-[#1d2025] hover:bg-[#282a30] text-xs text-[#b9cacb] hover:text-[#e2e2ea] border border-white/5 transition-colors"
                >
                  Show my discretionary spending headroom this week
                </button>
                <button 
                  onClick={() => {
                    setActionLocked(true);
                    alert('Locked purchase target to Sept 1 calendar');
                  }}
                  className="px-3 py-1 rounded-full bg-[#1d2025] hover:bg-[#282a30] text-xs text-[#b9cacb] hover:text-[#e2e2ea] border border-white/5 transition-colors"
                >
                  Lock purchase target to Sept 1 calendar
                </button>
              </div>
            </div>

            {/* Micro Action Bar */}
            <div className="flex items-center justify-between px-2">
              <div className="flex items-center gap-3 font-['JetBrains_Mono'] text-[10px] text-[#849495]">
                <span>FINPILOT V3.4 SYNTHESIS</span>
                <span>•</span>
                <span className="text-[#00e296]">ACCURACY SCORE: 99.4%</span>
              </div>

              <div className="flex items-center gap-1.5 text-[#849495]">
                <button className="p-1 hover:text-[#e2e2ea] transition-colors" title="Helpful">
                  <ThumbsUp className="w-3.5 h-3.5" />
                </button>
                <button className="p-1 hover:text-[#e2e2ea] transition-colors" title="Report inaccuracy">
                  <ThumbsDown className="w-3.5 h-3.5" />
                </button>
                <button 
                  onClick={handleCopyRationale}
                  className="p-1 hover:text-[#00f0ff] transition-colors relative" 
                  title="Copy rationale"
                >
                  <Copy className="w-3.5 h-3.5" />
                  {copied && (
                    <span className="absolute -top-6 -left-4 px-1.5 py-0.5 rounded bg-[#00f0ff] text-[#002d6e] text-[9px] font-['JetBrains_Mono'] font-bold">
                      Copied!
                    </span>
                  )}
                </button>
                <button className="p-1 hover:text-[#e2e2ea] transition-colors" title="Bookmark scenario">
                  <Bookmark className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Active Ledger Intelligence Strip */}
      <section className="p-4 rounded-2xl bg-[#191c21]/80 backdrop-blur-xl border border-white/5 flex flex-col gap-3 shadow-lg">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-2.5">
            <div className="p-1.5 rounded-lg bg-[#1d2025] text-[#00dbe9]">
              <CreditCard className="w-4 h-4" />
            </div>
            <div className="flex flex-col">
              <span className="font-['Plus_Jakarta_Sans'] text-xs font-semibold text-[#e2e2ea]">
                Active Ledger Ingest Queue
              </span>
              <span className="font-['JetBrains_Mono'] text-[10px] text-[#849495] uppercase">
                VERIFIED BANK STREAMS & DOCUMENT PARSING
              </span>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="px-2.5 py-1 rounded bg-[#282a30] text-[#00e296] font-['JetBrains_Mono'] text-[10px] flex items-center gap-1.5">
              <span className="h-1.5 w-1.5 rounded-full bg-[#00e296] animate-pulse"></span>
              HDFC SALARY LIVE
            </span>
            <span className="px-2.5 py-1 rounded bg-[#282a30] text-[#00dbe9] font-['JetBrains_Mono'] text-[10px]">
              ICICI CREDIT LIVE
            </span>
          </div>
        </div>

        {/* Ledger Mini Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-2.5">
          <div className="p-3 rounded-xl bg-[#282a30]/50 border border-white/5 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Building className="w-4 h-4 text-[#00f0ff]" />
              <div>
                <p className="text-xs font-medium text-[#e2e2ea]">Monthly Apartment Rent</p>
                <p className="font-['JetBrains_Mono'] text-[10px] text-[#849495]">Due in 3 days • Aug 28</p>
              </div>
            </div>
            <span className="font-['JetBrains_Mono'] text-xs font-semibold text-[#e2e2ea]">₹18,000</span>
          </div>

          <div className="p-3 rounded-xl bg-[#282a30]/50 border border-white/5 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Calendar className="w-4 h-4 text-[#b0c6ff]" />
              <div>
                <p className="text-xs font-medium text-[#e2e2ea]">Active Subscriptions</p>
                <p className="font-['JetBrains_Mono'] text-[10px] text-[#849495]">7 platforms queued</p>
              </div>
            </div>
            <span className="font-['JetBrains_Mono'] text-xs font-semibold text-[#e2e2ea]">₹4,000</span>
          </div>

          <div className="p-3 rounded-xl bg-[#282a30]/50 border border-white/5 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-[#00e296]" />
              <div>
                <p className="text-xs font-medium text-[#e2e2ea]">Anticipated Payroll</p>
                <p className="font-['JetBrains_Mono'] text-[10px] text-[#849495]">Scheduled Aug 31</p>
              </div>
            </div>
            <span className="font-['JetBrains_Mono'] text-xs font-semibold text-[#00e296]">+₹90,000</span>
          </div>
        </div>
      </section>

      {/* Persistent Bottom Chat Console & Multi-format File Drop Strip */}
      <div className="fixed bottom-3 left-0 lg:left-64 right-0 px-4 md:px-6 z-20 pointer-events-none">
        <div className="max-w-7xl mx-auto p-3 rounded-2xl bg-[#191c21]/95 border border-[#00f0ff]/30 backdrop-blur-2xl shadow-2xl flex flex-col gap-2 pointer-events-auto">
          {/* Controls Bar */}
          <div className="flex items-center justify-between px-1">
            <div className="flex items-center gap-2">
              <label className="cursor-pointer flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-[#1d2025] hover:bg-[#282a30] text-[#b9cacb] hover:text-[#e2e2ea] font-['JetBrains_Mono'] text-[10px] transition-colors">
                <Paperclip className="w-3.5 h-3.5 text-[#00f0ff]" />
                <span>ATTACH STATEMENT / RECEIPT</span>
                <input
                  type="file"
                  accept=".pdf,.csv,.xlsx,.png,.jpg"
                  className="hidden"
                  onChange={(e) => {
                    if (e.target.files && e.target.files[0]) {
                      setAttachedFile(e.target.files[0].name);
                    }
                  }}
                />
              </label>

              <button 
                onClick={() => alert('Voice dictation active. Listening...')}
                className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-[#1d2025] hover:bg-[#282a30] text-[#b9cacb] hover:text-[#e2e2ea] font-['JetBrains_Mono'] text-[10px] transition-colors"
              >
                <Mic className="w-3.5 h-3.5 text-[#b0c6ff]" />
                <span>VOICE DICTATION</span>
              </button>
            </div>

            {attachedFile && (
              <div className="font-['JetBrains_Mono'] text-[11px] text-[#00e296] flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>{attachedFile} (Parsed)</span>
                <button onClick={() => setAttachedFile(null)} className="ml-1 text-[#849495] hover:text-[#ffb4ab]">
                  <X className="w-3 h-3" />
                </button>
              </div>
            )}
          </div>

          {/* Main Input Textarea */}
          <div className="relative flex items-center">
            <textarea
              value={userPrompt}
              onChange={(e) => setUserPrompt(e.target.value)}
              placeholder="Ask FinPilot anything or drop PDF bank statements, CSV ledger exports, purchase invoices..."
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
                onClick={() => {
                  if (userPrompt.trim()) {
                    alert(`Query dispatched to FinPilot Neural Engine: "${userPrompt}"`);
                    setUserPrompt('');
                  }
                }}
                className="px-3.5 py-1.5 rounded-lg bg-gradient-to-r from-[#0068ed] to-[#00f0ff] text-[#002d6e] hover:brightness-110 font-['Plus_Jakarta_Sans'] text-xs font-bold transition-all flex items-center gap-1 shadow-md"
              >
                <span>Analyze</span>
                <ArrowUp className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          {/* Micro Telemetry Footer */}
          <div className="flex flex-wrap items-center justify-between px-1 text-[#849495] font-['JetBrains_Mono'] text-[10px]">
            <div className="flex items-center gap-2">
              <span>MODEL: SYNAPSE-4.2-FINANCIAL-ORCHESTRATOR</span>
              <span className="hidden sm:inline">•</span>
              <span className="hidden sm:inline">ZERO-RETENTION TRAINING GUARANTEE</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="h-1.5 w-1.5 rounded-full bg-[#00e296]"></span>
              <span>SYSTEM RUNWAY: OPTIMAL</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
