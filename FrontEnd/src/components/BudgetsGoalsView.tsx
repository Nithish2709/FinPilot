import React, { useState } from 'react';
import { PiggyBank, Target, TrendingUp, ShieldCheck, Sparkles, CheckCircle2 } from 'lucide-react';
import { ReserveVault } from '../types';

export const BudgetsGoalsView: React.FC = () => {
  const [vaults, setVaults] = useState<ReserveVault[]>([
    { id: '1', name: '6-Month Emergency Runway', current: 180000, target: 300000, targetDate: 'Dec 2025', percent: 60 },
    { id: '2', name: 'Electric Vehicle / Model 3 Downpayment', current: 95000, target: 150000, targetDate: 'March 2026', percent: 63 },
    { id: '3', name: 'Annual International Travel Buffer', current: 42000, target: 60000, targetDate: 'Nov 2025', percent: 70 },
    { id: '4', name: 'Hardware & Tech Upgrade Fund', current: 35000, target: 80000, targetDate: 'Oct 2025', percent: 44 }
  ]);

  return (
    <div className="flex flex-col gap-6 w-full max-w-7xl mx-auto pb-24">
      {/* Header Banner */}
      <div className="flex flex-wrap items-center justify-between gap-3 pt-2">
        <div className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-[#00f0ff] animate-pulse"></span>
          <span className="font-['JetBrains_Mono'] text-[11px] text-[#00f0ff] tracking-widest font-semibold uppercase">
            CAPITAL ALLOCATION & SINKING FUNDS
          </span>
        </div>
        <div className="flex items-center gap-2 font-['JetBrains_Mono'] text-xs text-[#849495]">
          <span>TOTAL TARGET ASSETS: <span className="text-[#00e296] font-bold">₹5,90,000</span></span>
        </div>
      </div>

      <div className="flex flex-col gap-1">
        <h1 className="font-['Plus_Jakarta_Sans'] text-2xl md:text-3xl font-bold text-[#dbfcff] tracking-tight">
          Budgets, Reserves & Goal Vectors
        </h1>
        <p className="text-sm text-[#b9cacb]">
          Deterministic goal trajectory engine modeling time-to-completion, monthly SIP contributions, and automated surplus transfers.
        </p>
      </div>

      {/* Vaults Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {vaults.map((vault) => (
          <div key={vault.id} className="p-5 rounded-2xl bg-[#191c21]/80 backdrop-blur-xl border border-white/5 flex flex-col gap-4 shadow-xl">
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-xl bg-[#1d2025] text-[#00f0ff]">
                  <PiggyBank className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-['Plus_Jakarta_Sans'] text-base font-bold text-[#dbfcff]">
                    {vault.name}
                  </h3>
                  <span className="font-['JetBrains_Mono'] text-xs text-[#849495]">
                    TARGET DATE: {vault.targetDate}
                  </span>
                </div>
              </div>
              <span className="font-['JetBrains_Mono'] text-lg font-bold text-[#00e296]">
                {vault.percent}%
              </span>
            </div>

            {/* Progress bar */}
            <div className="flex flex-col gap-1.5">
              <div className="w-full bg-[#111319] h-2.5 rounded-full overflow-hidden">
                <div 
                  className="bg-gradient-to-r from-[#0068ed] to-[#00f0ff] h-full rounded-full transition-all duration-500" 
                  style={{ width: `${vault.percent}%` }}
                ></div>
              </div>
              <div className="flex items-center justify-between font-['JetBrains_Mono'] text-xs text-[#849495]">
                <span>Saved: <strong className="text-[#e2e2ea]">₹{vault.current.toLocaleString('en-IN')}</strong></span>
                <span>Goal: <strong className="text-[#e2e2ea]">₹{vault.target.toLocaleString('en-IN')}</strong></span>
              </div>
            </div>

            <div className="flex items-center justify-between pt-2 border-t border-white/5 text-xs">
              <span className="text-[#b9cacb] flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-[#00dbe9]" />
                <span>Auto-SIP: ₹10,000/month</span>
              </span>

              <button 
                onClick={() => alert(`Added ₹5,000 surplus to ${vault.name}!`)}
                className="px-2.5 py-1 rounded bg-[#282a30] hover:bg-[#33353b] text-[#dbfcff] font-['JetBrains_Mono'] font-medium transition-colors"
              >
                + Allocate Surplus
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
