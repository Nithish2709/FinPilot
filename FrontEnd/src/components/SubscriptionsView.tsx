import React, { useState } from 'react';
import { Calendar, AlertTriangle, CheckCircle2, Trash2, ArrowUpRight, ShieldCheck, Plus, Sparkles } from 'lucide-react';
import { RecurringCommitment } from '../types';

export const SubscriptionsView: React.FC = () => {
  const [commitments, setCommitments] = useState<RecurringCommitment[]>([
    { id: '1', name: 'Netflix Premium (4K)', cost: 649, renewsIn: '6 days', notes: 'Usage: High (Watched 38 hrs in Aug)', category: 'Entertainment' },
    { id: '2', name: 'Spotify Family Plan', cost: 179, renewsIn: '14 days', notes: '5 user seats active • Daily playback', category: 'Entertainment' },
    { id: '3', name: 'GitHub Copilot Pro', cost: 850, renewsIn: '18 days', notes: 'Development AI accelerator', category: 'Developer Tools' },
    { id: '4', name: 'AWS Cloud Services', cost: 2420, renewsIn: 'Variable', notes: '+8% surge due to RDS test cluster', flagged: true, category: 'Cloud Infrastructure' },
    { id: '5', name: 'Cult.Fit Gym Elite Pass', cost: 2500, renewsIn: 'Monthly', notes: 'Auto-debit active • 24 check-ins logged', category: 'Health' },
    { id: '6', name: 'Apple iCloud+ 2TB', cost: 749, renewsIn: '22 days', notes: 'Family sharing • Photos & Device Backups', category: 'Cloud' },
    { id: '7', name: 'Amazon Prime Video', cost: 299, renewsIn: '9 days', notes: 'Flagged: Library overlap with Disney+ hotstar', flagged: true, category: 'Entertainment' }
  ]);

  const totalMonthly = commitments.reduce((acc, curr) => acc + curr.cost, 0);

  const handleDelete = (id: string) => {
    setCommitments(commitments.filter(c => c.id !== id));
  };

  return (
    <div className="flex flex-col gap-6 w-full max-w-7xl mx-auto pb-24">
      {/* Header Banner */}
      <div className="flex flex-wrap items-center justify-between gap-3 pt-2">
        <div className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-[#00f0ff] animate-pulse"></span>
          <span className="font-['JetBrains_Mono'] text-[11px] text-[#00f0ff] tracking-widest font-semibold uppercase">
            COMMITMENT RADAR // 7 ACTIVE RECURRING NODES
          </span>
        </div>
        <div className="flex items-center gap-2 font-['JetBrains_Mono'] text-xs text-[#849495]">
          <span>TOTAL COMMITTED: <span className="text-[#dbfcff] font-bold">₹{totalMonthly.toLocaleString('en-IN')}/MO</span></span>
        </div>
      </div>

      <div className="flex flex-col gap-1">
        <h1 className="font-['Plus_Jakarta_Sans'] text-2xl md:text-3xl font-bold text-[#dbfcff] tracking-tight">
          Subscriptions & Recurring Commitments
        </h1>
        <p className="text-sm text-[#b9cacb]">
          Autonomous monitoring of subscription renewal dates, price surges, duplicate services, and zero-usage zombie charges.
        </p>
      </div>

      {/* Flagged Zombies Card */}
      <div className="p-4 rounded-2xl bg-[#93000a]/20 border border-[#ffb4ab]/30 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-[#93000a]/40 text-[#ffb4ab]">
            <AlertTriangle className="w-5 h-5" />
          </div>
          <div>
            <h4 className="font-['Plus_Jakarta_Sans'] text-sm font-bold text-[#ffb4ab]">
              2 Potentially Redundant Subscriptions Detected
            </h4>
            <p className="text-xs text-[#b9cacb]">
              AWS test database idle for 12 days (+₹2,420/mo) and Amazon Prime duplicate streaming (+₹299/mo). Canceling saves <span className="text-[#00e296] font-bold">₹2,719/month</span>.
            </p>
          </div>
        </div>

        <button 
          onClick={() => {
            setCommitments(commitments.filter(c => !c.flagged));
            alert('Purged 2 flagged subscriptions. Saved ₹2,719/mo!');
          }}
          className="px-3.5 py-1.5 rounded-lg bg-[#93000a] hover:bg-[#93000a]/80 text-[#ffdad6] font-['JetBrains_Mono'] text-xs font-bold transition-colors"
        >
          Auto-Purge Flagged
        </button>
      </div>

      {/* Subscription Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {commitments.map((item) => (
          <div 
            key={item.id} 
            className={`p-4 rounded-2xl bg-[#191c21]/80 backdrop-blur-xl border transition-all flex flex-col justify-between gap-3 shadow-md ${
              item.flagged ? 'border-[#ffb4ab]/40 bg-[#93000a]/10' : 'border-white/5 hover:border-white/10'
            }`}
          >
            <div className="flex items-start justify-between">
              <div>
                <span className="font-['JetBrains_Mono'] text-[10px] text-[#849495] uppercase font-semibold">
                  {item.category}
                </span>
                <h3 className="font-['Plus_Jakarta_Sans'] text-sm font-bold text-[#e2e2ea]">
                  {item.name}
                </h3>
              </div>
              <div className="text-right">
                <span className="font-['JetBrains_Mono'] text-base font-bold text-[#dbfcff]">
                  ₹{item.cost}
                </span>
                <span className="font-['JetBrains_Mono'] text-[10px] text-[#849495] block">/mo</span>
              </div>
            </div>

            <p className="text-xs text-[#b9cacb] font-['JetBrains_Mono']">
              {item.notes}
            </p>

            <div className="flex items-center justify-between pt-2 border-t border-white/5 text-xs font-['JetBrains_Mono']">
              <span className="text-[#849495] flex items-center gap-1">
                <Calendar className="w-3.5 h-3.5 text-[#00f0ff]" />
                <span>{item.renewsIn}</span>
              </span>

              <button
                onClick={() => handleDelete(item.id)}
                className="text-[#849495] hover:text-[#ffb4ab] transition-colors p-1"
                title="Cancel subscription"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
