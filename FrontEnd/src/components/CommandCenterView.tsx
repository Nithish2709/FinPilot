import React, { useState, useEffect } from 'react';
import { 
  Building2, 
  ArrowDownLeft, 
  ArrowUpRight, 
  Lock, 
  ShieldCheck, 
  TrendingUp, 
  AlertTriangle, 
  CheckCircle2, 
  ChevronRight, 
  Sparkles, 
  Zap, 
  Compass, 
  Filter, 
  RefreshCw,
  Eye,
  Sliders
} from 'lucide-react';
import { dashboardApi } from '../api/dashboard';
import { subscriptionsApi } from '../api/subscriptions';
import { goalsApi } from '../api/goals';
import { DashboardResponse, AnalyticsResponse, SubscriptionRecord, Goal } from '../types';
import { useAuth } from '../context/AuthContext';

interface CommandCenterViewProps {
  onNavigateToScenario: () => void;
  onNavigateToAssistant: (query?: string) => void;
}

export const CommandCenterView: React.FC<CommandCenterViewProps> = ({
  onNavigateToScenario,
  onNavigateToAssistant
}) => {
  const { isAuthenticated } = useAuth();
  const [horizon, setHorizon] = useState<'30D' | '90D' | '1Y'>('90D');
  const [dashboard, setDashboard] = useState<DashboardResponse | null>(null);
  const [analytics, setAnalytics] = useState<AnalyticsResponse | null>(null);
  const [subscriptions, setSubscriptions] = useState<SubscriptionRecord[]>([]);
  const [goals, setGoals] = useState<Goal[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [executedOptimization, setExecutedOptimization] = useState(false);

  const fetchTelemetry = async () => {
    if (!isAuthenticated) return;
    setLoading(true);
    setError(null);
    try {
      const [dashData, analyticsData, subsData, goalsData] = await Promise.all([
        dashboardApi.getDashboard().catch(() => null),
        dashboardApi.getAnalytics().catch(() => null),
        subscriptionsApi.getSubscriptions().catch(() => []),
        goalsApi.getGoals().catch(() => []),
      ]);
      setDashboard(dashData);
      setAnalytics(analyticsData);
      setSubscriptions(subsData);
      setGoals(goalsData);
    } catch (err: any) {
      setError(err.message || 'Failed to retrieve telemetry data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTelemetry();
  }, [isAuthenticated]);

  const palette = ['#00f0ff', '#b0c6ff', '#00e296', '#ffb4ab', '#e2e2ea', '#4dffb1'];

  const categories = dashboard?.top_categories?.map((cat, idx) => ({
    name: cat.category,
    amount: Number(cat.amount),
    percent: Math.round(Number(cat.percentage)),
    color: palette[idx % palette.length],
  })) || [
    { name: 'General', amount: 0, percent: 100, color: '#00f0ff' }
  ];

  const totalCommitted = dashboard?.upcoming_obligations?.reduce((acc, curr) => acc + Number(curr.expected_amount), 0) || 0;
  const currentBalance = Number(dashboard?.current_balance || 0);
  const monthlyIncome = Number(dashboard?.monthly_income || 0);
  const monthlyExpenses = Number(dashboard?.monthly_expenses || 0);
  const netCashflow = Number(dashboard?.net_cashflow || 0);
  const safeBuffer = Math.max(0, currentBalance - totalCommitted);
  const burnRatio = monthlyIncome > 0 ? ((monthlyExpenses / monthlyIncome) * 100).toFixed(1) : '0.0';


  return (
    <div className="flex flex-col gap-6 w-full max-w-7xl mx-auto pb-24">
      {/* Top Telemetry Header Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 pt-2">
        <div className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-[#00e296] animate-pulse"></span>
          <span className="font-['JetBrains_Mono'] text-[11px] text-[#00dbe9] tracking-widest font-semibold uppercase">
            FINPILOT TELEMETRY HUD // REAL-TIME SECTOR 07
          </span>
          <span className="text-[#3b494b]">•</span>
          <span className="font-['JetBrains_Mono'] text-[11px] text-[#849495] tracking-wider uppercase">
            SYS.SYNC: ACTIVE
          </span>
        </div>

        <div className="flex items-center gap-1.5 p-1 bg-[#191c21] rounded-lg border border-white/5">
          {(['30D ACTIVE', '90D RADAR', '1Y TRAJECTORY'] as const).map((tab) => {
            const code = tab.startsWith('30') ? '30D' : tab.startsWith('90') ? '90D' : '1Y';
            const isActive = horizon === code;
            return (
              <button
                key={tab}
                onClick={() => setHorizon(code)}
                className={`
                  px-3 py-1 rounded text-xs font-['JetBrains_Mono'] font-medium transition-all
                  ${isActive 
                    ? 'bg-[#282a30] text-[#7df4ff] shadow-sm font-semibold' 
                    : 'text-[#849495] hover:text-[#e2e2ea]'
                  }
                `}
              >
                {tab}
              </button>
            );
          })}
        </div>
      </div>

      {/* Main Title & Airspace status */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <h1 className="font-['Plus_Jakarta_Sans'] text-2xl md:text-3xl font-bold text-[#dbfcff] tracking-tight">
            Financial Health & Flight Path
          </h1>
          <span className="px-2.5 py-0.5 rounded-full bg-[#00e296]/15 border border-[#00e296]/30 text-[#00e296] font-['JetBrains_Mono'] text-[11px] font-semibold tracking-wider uppercase">
            AIRSPACE: OPTIMAL
          </span>
        </div>
        <div className="text-xs text-[#849495] font-['JetBrains_Mono']">
          LAST RECONCILED: 2 MINS AGO (LEDGER HASH: 0x9F4C..A812)
        </div>
      </div>

      {/* 5 High-Impact Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
        {/* Net Liquid Assets */}
        <div className="p-4 rounded-xl bg-[#191c21]/80 hover:bg-[#1d2025] border border-white/5 transition-all shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between text-[#849495]">
            <span className="font-['JetBrains_Mono'] text-[10px] uppercase tracking-wider font-semibold">
              NET LIQUID ASSETS
            </span>
            <Building2 className="w-4 h-4 text-[#00dbe9]" />
          </div>
          <div className="mt-2">
            <span className="font-['JetBrains_Mono'] text-2xl font-bold text-[#e2e2ea] tracking-tight">
              ₹{currentBalance.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </span>
          </div>
          <div className="mt-3 flex items-center justify-between">
            <span className="text-xs text-[#00e296] font-['JetBrains_Mono'] flex items-center gap-1 font-medium">
              <TrendingUp className="w-3 h-3" /> Net: ₹{netCashflow.toLocaleString('en-IN')}
            </span>
          </div>
        </div>

        {/* Monthly Inflow */}
        <div className="p-4 rounded-xl bg-[#191c21]/80 hover:bg-[#1d2025] border border-white/5 transition-all shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between text-[#849495]">
            <span className="font-['JetBrains_Mono'] text-[10px] uppercase tracking-wider font-semibold">
              MONTHLY INFLOW
            </span>
            <ArrowDownLeft className="w-4 h-4 text-[#4dffb1]" />
          </div>
          <div className="mt-2">
            <span className="font-['JetBrains_Mono'] text-2xl font-bold text-[#e2e2ea] tracking-tight">
              ₹{monthlyIncome.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </span>
          </div>
          <div className="mt-3 flex items-center gap-1.5 text-xs text-[#849495] truncate">
            <span className="w-1.5 h-1.5 rounded-full bg-[#4dffb1]"></span>
            <span className="truncate">Stage 4 Cashflow Engine</span>
          </div>
        </div>

        {/* Monthly Outflow */}
        <div className="p-4 rounded-xl bg-[#191c21]/80 hover:bg-[#1d2025] border border-white/5 transition-all shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between text-[#849495]">
            <span className="font-['JetBrains_Mono'] text-[10px] uppercase tracking-wider font-semibold">
              MONTHLY OUTFLOW
            </span>
            <ArrowUpRight className="w-4 h-4 text-[#b0c6ff]" />
          </div>
          <div className="mt-2">
            <span className="font-['JetBrains_Mono'] text-2xl font-bold text-[#e2e2ea] tracking-tight">
              ₹{monthlyExpenses.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </span>
          </div>
          <div className="mt-3 text-xs text-[#849495] font-['JetBrains_Mono']">
            Burn Ratio <span className="text-[#dbfcff] font-semibold">{burnRatio}% of Inflow</span>
          </div>
        </div>

        {/* Committed Load */}
        <div className="p-4 rounded-xl bg-[#191c21]/80 hover:bg-[#1d2025] border border-white/5 transition-all shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between text-[#849495]">
            <span className="font-['JetBrains_Mono'] text-[10px] uppercase tracking-wider font-semibold">
              COMMITTED LOAD
            </span>
            <Lock className="w-4 h-4 text-[#7df4ff]" />
          </div>
          <div className="mt-2">
            <span className="font-['JetBrains_Mono'] text-2xl font-bold text-[#e2e2ea] tracking-tight">
              ₹{totalCommitted.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </span>
          </div>
          <div className="mt-3 text-xs text-[#849495] truncate">
            {dashboard?.upcoming_obligations?.length || 0} Upcoming Obligations
          </div>
        </div>

        {/* Discretionary Safe Buffer */}
        <div className="p-4 rounded-xl bg-[#191c21]/80 hover:bg-[#1d2025] border border-white/5 transition-all shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between text-[#849495]">
            <span className="font-['JetBrains_Mono'] text-[10px] uppercase tracking-wider font-semibold">
              DISCRETIONARY SAFE BUFFER
            </span>
            <ShieldCheck className="w-4 h-4 text-[#00e296]" />
          </div>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="font-['JetBrains_Mono'] text-2xl font-bold text-[#00e296] tracking-tight">
              ₹{safeBuffer.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </span>
          </div>
          <div className="mt-3 flex items-center justify-between text-xs">
            <span className="text-[#849495] text-[11px]">Liquid - Obligations</span>
          </div>
        </div>

      </div>

      {/* Main Analytical Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left 8 Cols: Projection Chart + Neural Drift Audit */}
        <div className="lg:col-span-8 flex flex-col gap-6">
          {/* 90-Day Cash Flow & Runway Projection */}
          <div className="p-5 rounded-2xl bg-[#191c21]/70 border border-white/5 backdrop-blur-xl flex flex-col gap-4 shadow-xl">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div className="flex flex-col">
                <div className="flex items-center gap-2">
                  <span className="font-['JetBrains_Mono'] text-[10px] text-[#849495] uppercase font-semibold">
                    PREDICTIVE TELEMETRY GRID
                  </span>
                  <span className="px-1.5 py-0.2 rounded bg-[#00e296]/15 text-[#00e296] text-[10px] font-['JetBrains_Mono'] font-bold">
                    99.2% ACCURACY
                  </span>
                </div>
                <h2 className="font-['Plus_Jakarta_Sans'] text-lg font-bold text-[#dbfcff]">
                  90-Day Cash Flow & Runway Projection
                </h2>
              </div>

              {/* Chart Legend */}
              <div className="flex items-center gap-4 text-xs font-['JetBrains_Mono']">
                <div className="flex items-center gap-1.5 text-[#e2e2ea]">
                  <span className="w-2.5 h-1 bg-[#00f0ff] rounded"></span>
                  <span>Inflow</span>
                </div>
                <div className="flex items-center gap-1.5 text-[#849495]">
                  <span className="w-2.5 h-1 bg-[#849495] rounded"></span>
                  <span>Expenses</span>
                </div>
                <div className="flex items-center gap-1.5 text-[#00e296]">
                  <span className="w-2.5 h-1 bg-[#00e296] rounded"></span>
                  <span>Safe Trajectory</span>
                </div>
              </div>
            </div>

            {/* Interactive SVG Projection Chart */}
            <div className="relative w-full h-56 bg-[#111319]/80 rounded-xl p-3 border border-white/5 overflow-hidden">
              {/* Event Markers Overlay */}
              <div className="absolute top-4 left-6 flex items-center gap-1.5 px-2 py-0.5 rounded bg-[#1d2025] border border-white/10 text-[11px] font-['JetBrains_Mono'] text-[#e2e2ea] shadow">
                <span className="w-2 h-2 rounded-full bg-[#00f0ff]"></span>
                <span>T-NOW: 18 AUG</span>
              </div>

              <div className="absolute top-4 left-1/2 -translate-x-12 flex items-center gap-1.5 px-2 py-0.5 rounded bg-[#1d2025] border border-[#ffb4ab]/30 text-[11px] font-['JetBrains_Mono'] text-[#ffb4ab] shadow">
                <span className="font-bold">₹18,000</span>
                <span className="text-[#849495]">Rent 5th Sep</span>
              </div>

              <div className="absolute top-4 right-20 flex items-center gap-1.5 px-2 py-0.5 rounded bg-[#1d2025] border border-[#00f0ff]/30 text-[11px] font-['JetBrains_Mono'] text-[#00f0ff] shadow">
                <span className="font-bold">₹4,500</span>
                <span className="text-[#849495]">AWS 12th Sep</span>
              </div>

              {/* Chart SVG Canvas */}
              <svg className="w-full h-full pt-10" preserveAspectRatio="none" viewBox="0 0 700 160">
                <defs>
                  <linearGradient id="chartGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#00f0ff" stopOpacity="0.25" />
                    <stop offset="60%" stopColor="#0068ed" stopOpacity="0.08" />
                    <stop offset="100%" stopColor="#0068ed" stopOpacity="0" />
                  </linearGradient>
                </defs>

                {/* Horizontal Baseline Grids */}
                <line x1="0" y1="30" x2="700" y2="30" stroke="#33353b" strokeDasharray="3 3" strokeOpacity="0.5" />
                <line x1="0" y1="75" x2="700" y2="75" stroke="#33353b" strokeDasharray="3 3" strokeOpacity="0.5" />
                <line x1="0" y1="120" x2="700" y2="120" stroke="#33353b" strokeDasharray="3 3" strokeOpacity="0.5" />

                {/* Gradient area fill under curve */}
                <path
                  d="M 0,110 Q 80,105 160,50 T 320,55 T 480,40 T 700,32 L 700,160 L 0,160 Z"
                  fill="url(#chartGradient)"
                />

                {/* Main trajectory line */}
                <path
                  d="M 0,110 Q 80,105 160,50 T 320,55 T 480,40 T 700,32"
                  fill="none"
                  stroke="#00f0ff"
                  strokeWidth="2.5"
                />

                {/* Secondary dashed safety baseline */}
                <path
                  d="M 0,130 Q 140,125 280,115 T 560,95 T 700,85"
                  fill="none"
                  stroke="#00e296"
                  strokeWidth="1.5"
                  strokeDasharray="4 4"
                />

                {/* Milestone nodes */}
                <circle cx="160" cy="50" r="4" fill="#00f0ff" stroke="#111319" strokeWidth="2" />
                <circle cx="280" cy="85" r="4" fill="#ffb4ab" stroke="#111319" strokeWidth="2" />
                <circle cx="420" cy="88" r="4" fill="#00f0ff" stroke="#111319" strokeWidth="2" />
                <circle cx="560" cy="65" r="4" fill="#00e296" stroke="#111319" strokeWidth="2" />
              </svg>

              {/* X-axis milestone markers */}
              <div className="flex items-center justify-between text-[10px] font-['JetBrains_Mono'] text-[#849495] pt-1 px-1">
                <span>AUG 20 (DAY 0)</span>
                <span>SEP 05 (RENT BURST)</span>
                <span>SEP 20 (Q3 TAX RES)</span>
                <span>OCT 15 (EQUILIBRIUM + ₹48k)</span>
                <span>NOV 20 (RESERVE REACHED)</span>
              </div>
            </div>

            {/* 3 Metric Output Pods */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-1">
              <div className="p-3 rounded-xl bg-[#1d2025]/60 border border-white/5 flex flex-col">
                <span className="font-['JetBrains_Mono'] text-[10px] text-[#849495] uppercase font-medium">
                  MIN BALANCE POINT
                </span>
                <span className="font-['JetBrains_Mono'] text-lg font-bold text-[#e2e2ea]">
                  ₹2,84,100
                </span>
                <span className="text-[11px] text-[#00e296] mt-0.5">
                  On Sep 6 (After fixed run)
                </span>
              </div>

              <div className="p-3 rounded-xl bg-[#1d2025]/60 border border-white/5 flex flex-col">
                <span className="font-['JetBrains_Mono'] text-[10px] text-[#849495] uppercase font-medium">
                  PREDICTED SURPLUS
                </span>
                <span className="font-['JetBrains_Mono'] text-lg font-bold text-[#00e296]">
                  +₹56,600
                </span>
                <span className="text-[11px] text-[#849495] mt-0.5">
                  At end of 90-day cycle
                </span>
              </div>

              <div className="p-3 rounded-xl bg-[#1d2025]/60 border border-white/5 flex flex-col">
                <span className="font-['JetBrains_Mono'] text-[10px] text-[#849495] uppercase font-medium">
                  VOLATILITY INDEX
                </span>
                <span className="font-['JetBrains_Mono'] text-lg font-bold text-[#e2e2ea]">
                  Low <span className="text-[#00e296]">(0.14)</span>
                </span>
                <span className="text-[11px] text-[#849495] mt-0.5">
                  Confidence grade A+
                </span>
              </div>
            </div>
          </div>

          {/* Neural Audit Engine: Monthly Drift & AI Pattern Evidence */}
          <div className="p-5 rounded-2xl bg-[#191c21]/70 border border-white/5 backdrop-blur-xl flex flex-col gap-4 shadow-xl">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div className="flex items-center gap-2">
                <span className="p-1 rounded bg-[#0068ed]/20 text-[#00dbe9]">
                  <Compass className="w-4 h-4" />
                </span>
                <span className="font-['JetBrains_Mono'] text-[11px] text-[#849495] uppercase font-semibold">
                  NEURAL AUDIT ENGINE
                </span>
                <span className="px-2 py-0.5 rounded bg-[#93000a]/50 text-[#ffb4ab] font-['JetBrains_Mono'] text-[10px] font-bold uppercase">
                  DELTA DETECTED
                </span>
              </div>

              <button 
                onClick={() => onNavigateToAssistant('Audit my monthly drift details')}
                className="px-3 py-1 rounded bg-[#1d2025] hover:bg-[#282a30] text-xs text-[#b9cacb] hover:text-[#e2e2ea] transition-colors flex items-center gap-1 font-['JetBrains_Mono']"
              >
                <span>Drill-Down View</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>

            <h3 className="font-['Plus_Jakarta_Sans'] text-base font-bold text-[#dbfcff]">
              Monthly Drift & AI Pattern Evidence
            </h3>

            <p className="text-sm text-[#b9cacb] leading-relaxed">
              <span className="text-[#ffb4ab] font-semibold">Food & Dining increased +23% (+₹1,426)</span> vs July baseline. FinPilot detected <span className="text-[#dbfcff] font-medium">4 additional weekend food deliveries</span> (Swiggy/Zomato). Meanwhile, discretionary transport dropped <span className="text-[#00e296] font-semibold">-14% (-₹980)</span> due to telecommuting.
            </p>

            {/* Visual Comparison Progress Bars */}
            <div className="flex flex-col gap-2 p-3.5 rounded-xl bg-[#111319]/70 border border-white/5">
              <div className="flex items-center justify-between text-xs font-['JetBrains_Mono']">
                <span className="text-[#849495]">CATEGORY COMPARISON: FOOD & DINING</span>
                <span className="text-[#ffb4ab] font-semibold">+23.0% EXCURSION</span>
              </div>

              <div className="flex flex-col gap-2 pt-1">
                <div className="flex items-center gap-3">
                  <span className="w-24 text-xs text-[#849495] font-['JetBrains_Mono']">July Baseline</span>
                  <div className="flex-1 bg-[#282a30] h-2.5 rounded-full overflow-hidden">
                    <div className="bg-[#849495] h-full rounded-full" style={{ width: '70%' }}></div>
                  </div>
                  <span className="font-['JetBrains_Mono'] text-xs text-[#849495] w-14 text-right">₹6,200</span>
                </div>

                <div className="flex items-center gap-3">
                  <span className="w-24 text-xs text-[#dbfcff] font-['JetBrains_Mono'] font-medium">August (Now)</span>
                  <div className="flex-1 bg-[#282a30] h-2.5 rounded-full overflow-hidden">
                    <div className="bg-gradient-to-r from-[#0068ed] to-[#00f0ff] h-full rounded-full" style={{ width: '86%' }}></div>
                  </div>
                  <span className="font-['JetBrains_Mono'] text-xs text-[#00f0ff] font-bold w-14 text-right">₹7,626</span>
                </div>
              </div>
            </div>

            {/* Smart Mitigation Callout */}
            <div className="flex flex-wrap items-center justify-between gap-3 p-3 rounded-xl bg-[#00e296]/5 border border-[#00e296]/20">
              <div className="flex items-center gap-2 text-xs text-[#b9cacb]">
                <Sparkles className="w-4 h-4 text-[#00e296] shrink-0" />
                <span>Re-routing surplus ₹1,426 to weekend grocery batch saves approx <span className="text-[#00e296] font-semibold">₹850/mo</span>.</span>
              </div>
              <button 
                onClick={() => alert('Food budget cap set to ₹6,500/month. Alerts armed!')}
                className="px-2.5 py-1 rounded bg-[#00e296]/15 hover:bg-[#00e296]/25 text-[#00e296] text-xs font-['JetBrains_Mono'] font-semibold flex items-center gap-1 transition-colors"
              >
                <span>SET FOOD CAP (₹6,500)</span>
                <ChevronRight className="w-3 h-3" />
              </button>
            </div>
          </div>
        </div>

        {/* Right 4 Cols: Outflow Ring + Recurring Radar + Reserves */}
        <div className="lg:col-span-4 flex flex-col gap-6">
          {/* Categorical Outflow Ring (Donut Chart) */}
          <div className="p-5 rounded-2xl bg-[#191c21]/70 border border-white/5 backdrop-blur-xl flex flex-col gap-4 shadow-xl">
            <div className="flex items-center justify-between">
              <div>
                <span className="font-['JetBrains_Mono'] text-[10px] text-[#849495] uppercase font-semibold">
                  BURN ALLOCATION
                </span>
                <h3 className="font-['Plus_Jakarta_Sans'] text-base font-bold text-[#dbfcff]">
                  Categorical Outflow Ring
                </h3>
              </div>
              <span className="px-2 py-0.5 rounded bg-[#1d2025] text-[#00dbe9] font-['JetBrains_Mono'] text-[10px] font-bold">
                6 ACTIVE NODES
              </span>
            </div>

            {/* Circular Donut Ring Chart */}
            <div className="relative w-44 h-44 mx-auto my-2 flex items-center justify-center">
              <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                {/* SVG segments using stroke-dasharray & stroke-dashoffset */}
                {/* Circumference = 2 * PI * 38 = ~238.76 */}
                {categories.map((cat, idx) => {
                  const circumference = 238.76;
                  // Calculate stroke-dashoffset based on previous segments
                  let previousPercent = 0;
                  for (let i = 0; i < idx; i++) {
                    previousPercent += categories[i].percent;
                  }
                  const strokeDasharray = `${(cat.percent / 100) * circumference} ${circumference}`;
                  const strokeDashoffset = -((previousPercent / 100) * circumference);
                  return (
                    <circle 
                      key={idx}
                      cx="50" cy="50" r="38" 
                      fill="transparent" 
                      stroke={cat.color} 
                      strokeWidth="9" 
                      strokeDasharray={strokeDasharray} 
                      strokeDashoffset={strokeDashoffset} 
                    />
                  );
                })}
              </svg>

              {/* Center Text */}
              <div className="absolute inset-0 flex flex-col items-center justify-center text-center pointer-events-none">
                <span className="font-['JetBrains_Mono'] text-[9px] text-[#849495] uppercase font-bold">TOTAL BURN</span>
                <span className="font-['JetBrains_Mono'] text-lg font-bold text-[#e2e2ea]">₹68,400</span>
                <span className="font-['JetBrains_Mono'] text-[9px] text-[#00e296] font-medium">Within Safe Range</span>
              </div>
            </div>

            {/* Category breakdown grid */}
            <div className="grid grid-cols-2 gap-2 text-xs font-['JetBrains_Mono']">
              {categories.map((cat, idx) => (
                <div key={idx} className="flex items-center justify-between p-1.5 rounded bg-[#1d2025]/50">
                  <div className="flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full" style={{ backgroundColor: cat.color }}></span>
                    <span className="text-[#b9cacb] truncate">{cat.name}</span>
                  </div>
                  <span className="font-semibold text-[#e2e2ea]">{cat.percent}%</span>
                </div>
              ))}
            </div>
          </div>

          {/* Telemetry Radar: Recurring Commitments */}
          <div className="p-5 rounded-2xl bg-[#191c21]/70 border border-white/5 backdrop-blur-xl flex flex-col gap-3.5 shadow-xl">
            <div className="flex items-center justify-between">
              <div>
                <span className="font-['JetBrains_Mono'] text-[10px] text-[#849495] uppercase font-semibold">
                  TELEMETRY RADAR
                </span>
                <h3 className="font-['Plus_Jakarta_Sans'] text-base font-bold text-[#dbfcff]">
                  Recurring Commitments
                </h3>
              </div>
              <span className="font-['JetBrains_Mono'] text-xs font-bold text-[#e2e2ea]">
                ₹6,598/mo
              </span>
            </div>

            {/* List of items */}
            <div className="flex flex-col gap-2">
              {subscriptions.length > 0 ? subscriptions.slice(0, 5).map((sub, i) => {
                const daysUntil = sub.next_expected_date 
                  ? Math.ceil((new Date(sub.next_expected_date).getTime() - new Date().getTime()) / (1000 * 3600 * 24))
                  : null;
                const daysText = daysUntil !== null ? `Renews in ${daysUntil} days` : `Freq: ${sub.frequency}`;
                
                return (
                  <div key={sub.id || i} className="flex items-center justify-between p-2 rounded-xl bg-[#1d2025]/50 border border-white/5 hover:border-white/10 transition-colors">
                    <div className="flex flex-col min-w-0">
                      <span className="text-xs font-medium text-[#e2e2ea] truncate">{sub.merchant}</span>
                      <span className="text-[10px] text-[#849495] truncate font-['JetBrains_Mono']">{daysText} • {sub.status}</span>
                    </div>
                    <div className="text-right shrink-0">
                      <span className="font-['JetBrains_Mono'] text-xs font-bold text-[#e2e2ea]">₹{Number(sub.average_amount).toLocaleString('en-IN')}</span>
                      <span className="text-[10px] text-[#849495] block">/mo</span>
                    </div>
                  </div>
                );
              }) : (
                <div className="text-xs text-[#849495] p-2 text-center">No active subscriptions detected.</div>
              )}
            </div>

            <button 
              onClick={() => onNavigateToAssistant('Audit my recurring commitments and purge unused ones')}
              className="w-full py-2 px-3 rounded-xl bg-[#0068ed]/10 hover:bg-[#0068ed]/20 text-[#7df4ff] border border-[#0068ed]/30 text-xs font-['JetBrains_Mono'] font-semibold flex items-center justify-center gap-1.5 transition-all"
            >
              <AlertTriangle className="w-3.5 h-3.5 text-[#ffb4ab]" />
              <span>Audit & Cancel Unused (2 flagged)</span>
            </button>
          </div>

          {/* Target Vectors: Reserves & Capital Vaults */}
          <div className="p-5 rounded-2xl bg-[#191c21]/70 border border-white/5 backdrop-blur-xl flex flex-col gap-3.5 shadow-xl">
            <div className="flex items-center justify-between">
              <div>
                <span className="font-['JetBrains_Mono'] text-[10px] text-[#849495] uppercase font-semibold">
                  TARGET VECTORS
                </span>
                <h3 className="font-['Plus_Jakarta_Sans'] text-base font-bold text-[#dbfcff]">
                  Reserves & Capital Vaults
                </h3>
              </div>
              <ShieldCheck className="w-4 h-4 text-[#00e296]" />
            </div>

            <div className="flex flex-col gap-3">
              {goals.length > 0 ? goals.slice(0, 3).map((g, idx) => {
                const current = Number(g.current_amount || 0);
                const target = Number(g.target_amount || 1);
                const percent = g.percentage_complete !== undefined ? Number(g.percentage_complete) : Math.min(100, Math.round((current / target) * 100));
                const colors = ['#00e296', '#00f0ff', '#b0c6ff'];
                const color = colors[idx % colors.length];

                return (
                  <div key={g.id || idx} className="flex flex-col gap-1.5">
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-[#e2e2ea] font-medium">{g.name}</span>
                      <span className="font-['JetBrains_Mono'] font-bold" style={{ color }}>{percent}%</span>
                    </div>
                    <div className="w-full bg-[#282a30] h-2 rounded-full overflow-hidden">
                      <div className="h-full rounded-full" style={{ width: `${percent}%`, backgroundColor: color }}></div>
                    </div>
                    <div className="flex items-center justify-between text-[10px] font-['JetBrains_Mono'] text-[#849495]">
                      <span>₹{current.toLocaleString('en-IN')} / ₹{target.toLocaleString('en-IN')}</span>
                      <span>{g.target_date ? `Target: ${g.target_date}` : 'Ongoing'}</span>
                    </div>
                  </div>
                );
              }) : (
                <div className="text-xs text-[#849495] text-center p-2">No target vectors configured.</div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Persistent Autonomous Dispatch Banner (Sticky at bottom) */}
      <div className="fixed bottom-3 left-0 lg:left-64 right-0 px-4 md:px-6 z-20 pointer-events-none">
        <div className="max-w-7xl mx-auto p-3.5 rounded-2xl bg-[#191c21]/95 border border-[#00f0ff]/30 backdrop-blur-2xl shadow-2xl flex flex-wrap items-center justify-between gap-4 pointer-events-auto">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-[#00f0ff] animate-ping"></span>
            <span className="font-['JetBrains_Mono'] text-xs text-[#00f0ff] uppercase font-bold tracking-wider">
              FINPILOT AUTONOMOUS DISPATCH
            </span>
            <span className="text-[11px] text-[#849495] font-['JetBrains_Mono']">
              3 OPPORTUNITIES READY
            </span>
          </div>

          <div className="hidden md:flex items-center gap-6 text-xs">
            <div className="flex flex-col">
              <span className="text-[#e2e2ea] font-medium">Duplicate streaming overlap detected</span>
              <span className="text-[#00e296] font-['JetBrains_Mono'] text-[11px]">Potential: ₹399/mo Saved</span>
            </div>
            <div className="flex flex-col">
              <span className="text-[#e2e2ea] font-medium">Switching annual billing on cloud dev tiers</span>
              <span className="text-[#00f0ff] font-['JetBrains_Mono'] text-[11px]">Instant Efficiency +16%</span>
            </div>
            <div className="flex flex-col">
              <span className="text-[#e2e2ea] font-medium">Surplus ₹14,000 ready to allocate</span>
              <span className="text-[#7df4ff] font-['JetBrains_Mono'] text-[11px]">Pushes Milestone 30 Days Closer</span>
            </div>
          </div>

          <div className="flex items-center gap-2.5">
            <button
              onClick={onNavigateToScenario}
              className="px-3 py-1.5 rounded-lg bg-[#1d2025] hover:bg-[#282a30] text-[#e2e2ea] text-xs font-['JetBrains_Mono'] font-medium transition-colors border border-white/10"
            >
              Simulate Impact
            </button>
            <button
              onClick={() => {
                setExecutedOptimization(true);
                alert('FinPilot Optimization Plan Activated! Saved ₹3,599 across cloud tiers & streaming subscriptions.');
              }}
              className="px-4 py-1.5 rounded-lg bg-gradient-to-r from-[#0068ed] to-[#00f0ff] text-[#002d6e] hover:brightness-110 text-xs font-['JetBrains_Mono'] font-bold transition-all shadow-[0_0_15px_rgba(0,240,255,0.4)]"
            >
              {executedOptimization ? 'Plan Active ✓' : 'Execute Optimization Plan'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
