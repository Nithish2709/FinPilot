import React, { useState } from 'react';
import { 
  GitBranch, 
  AlertTriangle, 
  CheckCircle2, 
  TrendingDown, 
  TrendingUp, 
  Clock, 
  Sliders, 
  CreditCard, 
  Calendar, 
  ShieldAlert, 
  ShieldCheck, 
  ArrowRight, 
  Lock, 
  RefreshCw,
  BellRing
} from 'lucide-react';

export const ScenarioEngineView: React.FC = () => {
  const [assetName, setAssetName] = useState('Pro Developer Laptop 16-inch');
  const [amount, setAmount] = useState<number>(60000);
  const [plannedDate, setPlannedDate] = useState('2025-08-24');
  const [protocol, setProtocol] = useState<'cash' | 'emi-3m' | 'wait-inflow'>('cash');
  const [lockedBeta, setLockedBeta] = useState(false);
  const [forcedAlpha, setForcedAlpha] = useState(false);

  // Dynamic calculations
  const startingLiquidity = 85000;
  const committedObligations = 22000;
  const payrollCredit = 90000;

  // Scenario Alpha (Buy Today)
  const alphaCost = protocol === 'emi-3m' ? Math.round(amount / 3) : amount;
  const alphaBuffer = startingLiquidity - committedObligations - alphaCost;
  const alphaRatio = ((alphaBuffer / startingLiquidity) * 100).toFixed(1);

  // Scenario Beta (Wait for Inflow on Sept 1)
  const betaCost = amount;
  const betaBuffer = startingLiquidity - committedObligations + payrollCredit - betaCost;
  const betaRatio = ((betaBuffer / (startingLiquidity + payrollCredit - committedObligations)) * 100).toFixed(1);

  return (
    <div className="flex flex-col gap-6 w-full max-w-7xl mx-auto pb-24">
      {/* Top Banner */}
      <div className="flex flex-wrap items-center justify-between gap-3 pt-2">
        <div className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-[#00f0ff] animate-pulse"></span>
          <span className="font-['JetBrains_Mono'] text-[11px] text-[#00f0ff] tracking-widest font-semibold uppercase">
            MODULE // SCENARIO-047 NEURAL PROJECTION ENGINE ACTIVE
          </span>
        </div>
        <div className="flex items-center gap-2 font-['JetBrains_Mono'] text-xs text-[#849495]">
          <span>CONFIDENCE SCORE: 99.1%</span>
          <span>•</span>
          <span className="text-[#00e296]">SIMULATION ENGINE RUNNING</span>
        </div>
      </div>

      {/* Main Header */}
      <div className="flex flex-col gap-1">
        <h1 className="font-['Plus_Jakarta_Sans'] text-2xl md:text-3xl font-bold text-[#dbfcff] tracking-tight">
          Purchase Impact & Buffer Simulation
        </h1>
        <p className="text-sm text-[#b9cacb]">
          Deterministic stress-testing of discretionary CapEx against committed liabilities, payroll cycles, and volatility thresholds.
        </p>
      </div>

      {/* Telemetry Input Console */}
      <div className="p-5 rounded-2xl bg-[#191c21]/80 backdrop-blur-xl border border-white/5 flex flex-col gap-4 shadow-xl">
        <div className="flex items-center justify-between pb-2 border-b border-white/5">
          <span className="font-['JetBrains_Mono'] text-[10px] text-[#849495] uppercase font-semibold">
            TELEMETRY INPUT PARAMETERS
          </span>
          <span className="font-['JetBrains_Mono'] text-[10px] text-[#00dbe9]">
            REAL-TIME RECOMPUTATION
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Target Asset */}
          <div className="flex flex-col gap-1.5">
            <label className="font-['JetBrains_Mono'] text-[11px] text-[#849495] uppercase font-medium">
              Target Asset / Purchase
            </label>
            <input
              type="text"
              value={assetName}
              onChange={(e) => setAssetName(e.target.value)}
              className="bg-[#111319] text-[#e2e2ea] text-xs font-semibold p-2.5 rounded-xl border border-white/10 focus:border-[#00f0ff] focus:outline-none"
            />
          </div>

          {/* Simulated Impact Sum */}
          <div className="flex flex-col gap-1.5">
            <label className="font-['JetBrains_Mono'] text-[11px] text-[#849495] uppercase font-medium">
              Simulated Impact Sum (₹)
            </label>
            <input
              type="number"
              value={amount}
              step={1000}
              onChange={(e) => setAmount(Number(e.target.value))}
              className="bg-[#111319] text-[#00f0ff] font-['JetBrains_Mono'] text-sm font-bold p-2.5 rounded-xl border border-white/10 focus:border-[#00f0ff] focus:outline-none"
            />
          </div>

          {/* Planned Date */}
          <div className="flex flex-col gap-1.5">
            <label className="font-['JetBrains_Mono'] text-[11px] text-[#849495] uppercase font-medium">
              Planned Purchase Date
            </label>
            <input
              type="date"
              value={plannedDate}
              onChange={(e) => setPlannedDate(e.target.value)}
              className="bg-[#111319] text-[#e2e2ea] text-xs font-['JetBrains_Mono'] p-2.5 rounded-xl border border-white/10 focus:border-[#00f0ff] focus:outline-none"
            />
          </div>

          {/* Allocation Bucket */}
          <div className="flex flex-col gap-1.5">
            <label className="font-['JetBrains_Mono'] text-[11px] text-[#849495] uppercase font-medium">
              Allocation Bucket
            </label>
            <select
              className="bg-[#111319] text-[#e2e2ea] text-xs font-medium p-2.5 rounded-xl border border-white/10 focus:border-[#00f0ff] focus:outline-none"
            >
              <option>CapEx / Hardware (Discretionary)</option>
              <option>Annual Sinking Fund</option>
              <option>Career Growth & Professional Setup</option>
            </select>
          </div>
        </div>

        {/* Execution Protocol Tabs */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-2">
          <span className="font-['JetBrains_Mono'] text-xs text-[#849495]">EXECUTION PROTOCOL:</span>
          <div className="flex flex-wrap items-center gap-2">
            {[
              { id: 'cash', label: 'Direct Outright Cash' },
              { id: 'emi-3m', label: '3M No-Cost EMI (₹20k/mo)' },
              { id: 'wait-inflow', label: 'Wait for Next Inflow' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setProtocol(tab.id as any)}
                className={`
                  px-3 py-1.5 rounded-lg text-xs font-['JetBrains_Mono'] font-medium transition-all
                  ${protocol === tab.id
                    ? 'bg-[#00f0ff]/20 text-[#00f0ff] border border-[#00f0ff]/40 shadow-sm'
                    : 'bg-[#111319] text-[#849495] hover:text-[#e2e2ea] border border-white/5'
                  }
                `}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Dual Comparative Scenario Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Scenario Alpha: Buy Today */}
        <div className="p-6 rounded-2xl bg-[#191c21]/80 backdrop-blur-xl border border-[#ffb4ab]/30 flex flex-col justify-between gap-6 shadow-xl relative overflow-hidden">
          <div className="flex flex-col gap-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="p-1.5 rounded-lg bg-[#93000a]/40 text-[#ffb4ab]">
                  <ShieldAlert className="w-4 h-4" />
                </span>
                <span className="font-['Plus_Jakarta_Sans'] text-base font-bold text-[#ffb4ab]">
                  SCENARIO ALPHA (BUY TODAY - CASH)
                </span>
              </div>
              <span className="px-2.5 py-0.5 rounded bg-[#93000a]/50 text-[#ffb4ab] font-['JetBrains_Mono'] text-[10px] font-bold uppercase">
                HIGH RISK
              </span>
            </div>

            {/* Gauge & Metrics */}
            <div className="flex items-center gap-6 p-4 rounded-xl bg-[#111319]/80 border border-white/5">
              {/* Circular Gauge */}
              <div className="relative w-20 h-20 shrink-0 flex items-center justify-center">
                <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
                  <path
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                    fill="none"
                    stroke="#282a30"
                    strokeWidth="3.5"
                  />
                  <path
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                    fill="none"
                    stroke="#ffb4ab"
                    strokeWidth="3.5"
                    strokeDasharray={`${Math.max(5, Math.min(100, Number(alphaRatio)))}, 100`}
                  />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="font-['JetBrains_Mono'] text-sm font-bold text-[#ffb4ab]">
                    {alphaRatio}%
                  </span>
                  <span className="font-['JetBrains_Mono'] text-[8px] text-[#849495] uppercase">
                    Buffer
                  </span>
                </div>
              </div>

              <div className="flex flex-col">
                <span className="font-['JetBrains_Mono'] text-[10px] text-[#849495] uppercase font-semibold">
                  PROJECTED BUFFER (AUG 24-30)
                </span>
                <span className="font-['JetBrains_Mono'] text-3xl font-bold text-[#ffb4ab]">
                  {alphaBuffer < 0 ? `-₹${Math.abs(alphaBuffer).toLocaleString('en-IN')}` : `₹${alphaBuffer.toLocaleString('en-IN')}`}
                </span>
                <span className="text-xs text-[#ffb4ab] mt-1 font-medium">
                  Safety Alert: Critical 3.5% liquidity margin
                </span>
              </div>
            </div>

            {/* Waterfall Ledger Breakdown */}
            <div className="flex flex-col gap-2 p-3.5 rounded-xl bg-[#1d2025]/50 border border-white/5 font-['JetBrains_Mono'] text-xs">
              <div className="flex justify-between text-[#849495]">
                <span>Starting Liquid Reserves</span>
                <span className="text-[#e2e2ea]">₹{startingLiquidity.toLocaleString('en-IN')}</span>
              </div>
              <div className="flex justify-between text-[#849495]">
                <span>Committed Obligations (Aug 25-30)</span>
                <span className="text-[#ffb4ab]">-₹{committedObligations.toLocaleString('en-IN')}</span>
              </div>
              <div className="flex justify-between text-[#849495]">
                <span>Proposed CapEx Deduction</span>
                <span className="text-[#ffb4ab]">-₹{alphaCost.toLocaleString('en-IN')}</span>
              </div>
              <div className="pt-2 border-t border-white/5 flex justify-between font-bold text-sm">
                <span className="text-[#dbfcff]">Net Unallocated Buffer</span>
                <span className="text-[#ffb4ab]">₹{alphaBuffer.toLocaleString('en-IN')}</span>
              </div>
            </div>

            {/* Critical AI Signals */}
            <div className="flex flex-col gap-2 text-xs text-[#b9cacb]">
              <div className="flex items-start gap-2">
                <AlertTriangle className="w-4 h-4 text-[#ffb4ab] shrink-0 mt-0.5" />
                <span>4-day exposure window with only ₹3,000 headroom before Aug 31 payroll.</span>
              </div>
              <div className="flex items-start gap-2">
                <AlertTriangle className="w-4 h-4 text-[#ffb4ab] shrink-0 mt-0.5" />
                <span>Any unexpected incident (medical, transit repair) forces high-interest credit card debt.</span>
              </div>
              <div className="flex items-start gap-2">
                <AlertTriangle className="w-4 h-4 text-[#ffb4ab] shrink-0 mt-0.5" />
                <span>Fails the 15% Recommended Emergency Cushion Test.</span>
              </div>
            </div>
          </div>

          <button
            onClick={() => {
              if (confirm('Warning: Scenario Alpha reduces safety buffer to 3.5%. Authorize anyway?')) {
                setForcedAlpha(true);
              }
            }}
            className="w-full py-2.5 px-4 rounded-xl bg-[#93000a]/40 hover:bg-[#93000a]/60 text-[#ffb4ab] border border-[#ffb4ab]/40 font-['JetBrains_Mono'] text-xs font-bold transition-all flex items-center justify-center gap-2"
          >
            <span>{forcedAlpha ? 'Authorized (High Exposure Flagged)' : 'Force Authorize Anyway (Not Recommended)'}</span>
          </button>
        </div>

        {/* Scenario Beta: Wait for Next Inflow */}
        <div className="p-6 rounded-2xl bg-[#191c21]/90 backdrop-blur-xl border border-[#00e296]/40 flex flex-col justify-between gap-6 shadow-2xl relative overflow-hidden">
          <div className="flex flex-col gap-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="p-1.5 rounded-lg bg-[#00e296]/20 text-[#00e296]">
                  <ShieldCheck className="w-4 h-4" />
                </span>
                <span className="font-['Plus_Jakarta_Sans'] text-base font-bold text-[#00f0ff]">
                  SCENARIO BETA (WAIT 8 DAYS - AI CHOICE)
                </span>
              </div>
              <span className="px-2.5 py-0.5 rounded bg-[#00e296]/20 text-[#00e296] font-['JetBrains_Mono'] text-[10px] font-bold uppercase">
                RECOMMENDED
              </span>
            </div>

            {/* Gauge & Metrics */}
            <div className="flex items-center gap-6 p-4 rounded-xl bg-[#111319]/80 border border-white/5">
              {/* Circular Gauge */}
              <div className="relative w-20 h-20 shrink-0 flex items-center justify-center">
                <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
                  <path
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                    fill="none"
                    stroke="#282a30"
                    strokeWidth="3.5"
                  />
                  <path
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                    fill="none"
                    stroke="#00e296"
                    strokeWidth="3.5"
                    strokeDasharray="98, 100"
                  />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="font-['JetBrains_Mono'] text-sm font-bold text-[#00e296]">
                    98%
                  </span>
                  <span className="font-['JetBrains_Mono'] text-[8px] text-[#849495] uppercase">
                    Confidence
                  </span>
                </div>
              </div>

              <div className="flex flex-col">
                <span className="font-['JetBrains_Mono'] text-[10px] text-[#849495] uppercase font-semibold">
                  PROJECTED BUFFER (SEPT 1)
                </span>
                <span className="font-['JetBrains_Mono'] text-3xl font-bold text-[#00e296]">
                  ₹{betaBuffer.toLocaleString('en-IN')}
                </span>
                <span className="text-xs text-[#00e296] mt-1 font-medium">
                  Safe Cushion: {betaRatio}% robust liquidity ratio
                </span>
              </div>
            </div>

            {/* Waterfall Ledger Breakdown */}
            <div className="flex flex-col gap-2 p-3.5 rounded-xl bg-[#1d2025]/50 border border-white/5 font-['JetBrains_Mono'] text-xs">
              <div className="flex justify-between text-[#849495]">
                <span>Starting Liquid Reserves</span>
                <span className="text-[#e2e2ea]">₹{startingLiquidity.toLocaleString('en-IN')}</span>
              </div>
              <div className="flex justify-between text-[#849495]">
                <span>Committed Obligations</span>
                <span className="text-[#b0c6ff]">-₹{committedObligations.toLocaleString('en-IN')}</span>
              </div>
              <div className="flex justify-between text-[#849495]">
                <span>Payroll Credit (Aug 31)</span>
                <span className="text-[#00e296]">+₹{payrollCredit.toLocaleString('en-IN')}</span>
              </div>
              <div className="flex justify-between text-[#849495]">
                <span>Proposed CapEx Deduction</span>
                <span className="text-[#ffb4ab]">-₹{betaCost.toLocaleString('en-IN')}</span>
              </div>
              <div className="pt-2 border-t border-white/5 flex justify-between font-bold text-sm">
                <span className="text-[#dbfcff]">Net Post-Tx Buffer</span>
                <span className="text-[#00e296]">₹{betaBuffer.toLocaleString('en-IN')}</span>
              </div>
            </div>

            {/* AI Optimization Insights */}
            <div className="flex flex-col gap-2 text-xs text-[#b9cacb]">
              <div className="flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-[#00e296] shrink-0 mt-0.5" />
                <span>Preserves full emergency fund intact with zero drawdowns.</span>
              </div>
              <div className="flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-[#00e296] shrink-0 mt-0.5" />
                <span>Maintains 4.8 months total runway post-purchase without lifestyle compromise.</span>
              </div>
              <div className="flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-[#00e296] shrink-0 mt-0.5" />
                <span>Credit score risk = 0; Zero interest expense or recurring debt drag.</span>
              </div>
            </div>
          </div>

          <button
            onClick={() => {
              setLockedBeta(true);
              alert('Scenario Beta Locked! Inflow alert set for Aug 31 with automated notification on Sept 1st.');
            }}
            className="w-full py-2.5 px-4 rounded-xl bg-gradient-to-r from-[#0068ed] to-[#00f0ff] text-[#002d6e] hover:brightness-110 font-['Plus_Jakarta_Sans'] text-xs font-bold transition-all flex items-center justify-center gap-2 shadow-[0_0_20px_rgba(0,240,255,0.4)]"
          >
            <BellRing className="w-4 h-4" />
            <span>{lockedBeta ? 'Scenario Beta Locked ✓ (Alert Armed)' : 'Lock Scenario Beta & Set Inflow Alert'}</span>
          </button>
        </div>
      </div>

      {/* Dynamic Trajectory Matrix SVG Comparison */}
      <div className="p-5 rounded-2xl bg-[#191c21]/80 backdrop-blur-xl border border-white/5 flex flex-col gap-4 shadow-xl">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div>
            <span className="font-['JetBrains_Mono'] text-[10px] text-[#849495] uppercase font-semibold">
              DYNAMIC TRAJECTORY MATRIX
            </span>
            <h3 className="font-['Plus_Jakarta_Sans'] text-base font-bold text-[#dbfcff]">
              Balance Vector Aug 24 - Oct 01
            </h3>
          </div>

          <div className="flex items-center gap-4 text-xs font-['JetBrains_Mono']">
            <div className="flex items-center gap-1.5 text-[#ffb4ab]">
              <span className="w-2.5 h-1 bg-[#ffb4ab] rounded"></span>
              <span>Scenario Alpha (Buy Today)</span>
            </div>
            <div className="flex items-center gap-1.5 text-[#00e296]">
              <span className="w-2.5 h-1 bg-[#00e296] rounded"></span>
              <span>Scenario Beta (Wait 8 Days)</span>
            </div>
          </div>
        </div>

        {/* Comparison SVG Chart */}
        <div className="relative w-full h-52 bg-[#111319]/80 rounded-xl p-3 border border-white/5 overflow-hidden">
          <svg className="w-full h-full pt-8" preserveAspectRatio="none" viewBox="0 0 600 120">
            {/* Critical Threshold line */}
            <line x1="0" y1="95" x2="600" y2="95" stroke="#ffb4ab" strokeDasharray="3 3" strokeOpacity="0.4" />
            <text x="10" y="90" fill="#ffb4ab" fontSize="9" fontFamily="monospace">CRITICAL SAFETY THRESHOLD (₹20,000)</text>

            {/* Salary credit point */}
            <line x1="280" y1="0" x2="280" y2="120" stroke="#00dbe9" strokeDasharray="2 2" strokeOpacity="0.4" />
            <text x="285" y="20" fill="#00dbe9" fontSize="9" fontFamily="monospace">AUG 31 PAYROLL (+₹90k)</text>

            {/* Scenario Alpha Line (Red Dips low) */}
            <path
              d="M 0,40 L 80,105 L 280,105 L 320,30 L 600,28"
              fill="none"
              stroke="#ffb4ab"
              strokeWidth="2.5"
            />

            {/* Scenario Beta Line (Stays healthy, dips post payroll) */}
            <path
              d="M 0,40 L 270,55 L 300,10 L 340,42 L 600,38"
              fill="none"
              stroke="#00e296"
              strokeWidth="2.5"
            />

            <circle cx="80" cy="105" r="4" fill="#ffb4ab" />
            <circle cx="340" cy="42" r="4" fill="#00e296" />
          </svg>

          {/* X Axis */}
          <div className="flex items-center justify-between text-[10px] font-['JetBrains_Mono'] text-[#849495] pt-1 px-1">
            <span>AUG 24 (TODAY)</span>
            <span>AUG 27 (RENT CYCLE)</span>
            <span>AUG 31 (PAYROLL)</span>
            <span>SEPT 01 (SCENARIO B PURCHASE)</span>
            <span>OCT 01 (EQUILIBRIUM)</span>
          </div>
        </div>
      </div>
    </div>
  );
};
