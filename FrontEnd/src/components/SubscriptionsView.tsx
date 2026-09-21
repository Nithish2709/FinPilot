import React, { useState, useEffect } from 'react';
import { Calendar, AlertTriangle, CheckCircle2, Trash2, ArrowUpRight, ShieldCheck, Plus, Sparkles, RefreshCw } from 'lucide-react';
import { subscriptionsApi } from '../api/subscriptions';
import { SubscriptionRecord } from '../types';
import { useAuth } from '../context/AuthContext';

export const SubscriptionsView: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const [commitments, setCommitments] = useState<SubscriptionRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const [detecting, setDetecting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchSubscriptions = async () => {
    if (!isAuthenticated) return;
    setLoading(true);
    setError(null);
    try {
      const data = await subscriptionsApi.getSubscriptions();
      setCommitments(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load subscriptions');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSubscriptions();
  }, [isAuthenticated]);

  const handleRunDetection = async () => {
    setDetecting(true);
    try {
      const res = await subscriptionsApi.detectSubscriptions();
      alert(`Cadence analysis completed: ${res.message}`);
      fetchSubscriptions();
    } catch (err: any) {
      alert(err.message || 'Detection failed');
    } finally {
      setDetecting(false);
    }
  };

  const totalMonthly = commitments.reduce((acc, curr) => acc + Number(curr.average_amount), 0);

  return (
    <div className="flex flex-col gap-6 w-full max-w-7xl mx-auto pb-24">
      {/* Header Banner */}
      <div className="flex flex-wrap items-center justify-between gap-3 pt-2">
        <div className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-[#00f0ff] animate-pulse"></span>
          <span className="font-['JetBrains_Mono'] text-[11px] text-[#00f0ff] tracking-widest font-semibold uppercase">
            STAGE 4 & STAGE 9 RECURRING ENGINE // {commitments.length} DETECTED
          </span>
        </div>
        <div className="flex items-center gap-2 font-['JetBrains_Mono'] text-xs text-[#849495]">
          <span>TOTAL COMMITTED: <span className="text-[#dbfcff] font-bold">₹{totalMonthly.toLocaleString('en-IN')}/MO</span></span>
        </div>
      </div>

      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-col gap-1">
          <h1 className="font-['Plus_Jakarta_Sans'] text-2xl md:text-3xl font-bold text-[#dbfcff] tracking-tight">
            Subscriptions & Recurring Commitments
          </h1>
          <p className="text-sm text-[#b9cacb]">
            Deterministic cadence detection analyzing merchant regularity, intervals, and amount variance.
          </p>
        </div>

        <button
          onClick={handleRunDetection}
          disabled={detecting}
          className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-gradient-to-r from-[#0068ed] to-[#00f0ff] text-[#002d6e] hover:brightness-110 text-xs font-bold font-['JetBrains_Mono'] transition-all shadow-[0_0_15px_rgba(0,240,255,0.4)] disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${detecting ? 'animate-spin' : ''}`} />
          <span>{detecting ? 'Analyzing Intervals...' : 'Run Cadence Detector'}</span>
        </button>
      </div>

      {error && (
        <div className="p-3 rounded-xl bg-[#93000a]/20 border border-[#ffb4ab]/40 text-[#ffb4ab] text-xs flex items-center gap-2">
          <AlertTriangle className="w-4 h-4" />
          <span>{error}</span>
        </div>
      )}

      {/* Subscription Grid */}
      {commitments.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {commitments.map((item) => (
            <div 
              key={item.id} 
              className="p-4 rounded-2xl bg-[#191c21]/80 backdrop-blur-xl border border-white/5 hover:border-white/10 transition-all flex flex-col justify-between gap-3 shadow-md"
            >
              <div className="flex items-start justify-between">
                <div>
                  <span className="font-['JetBrains_Mono'] text-[10px] text-[#849495] uppercase font-semibold">
                    Confidence: {(Number(item.confidence) * 100).toFixed(0)}%
                  </span>
                  <h3 className="font-['Plus_Jakarta_Sans'] text-sm font-bold text-[#e2e2ea]">
                    {item.merchant}
                  </h3>
                </div>
                <div className="text-right">
                  <span className="font-['JetBrains_Mono'] text-base font-bold text-[#dbfcff]">
                    ₹{Number(item.average_amount).toLocaleString('en-IN')}
                  </span>
                  <span className="font-['JetBrains_Mono'] text-[10px] text-[#849495] block">/avg</span>
                </div>
              </div>

              <div className="flex items-center justify-between pt-2 border-t border-white/5 text-xs font-['JetBrains_Mono']">
                <span className="text-[#849495] flex items-center gap-1">
                  <Calendar className="w-3.5 h-3.5 text-[#00f0ff]" />
                  <span>Cadence: {item.frequency}</span>
                </span>
                <span className="text-[#00e296] text-[10px] font-bold uppercase">{item.status}</span>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="p-12 text-center bg-[#191c21]/40 border border-dashed border-white/10 rounded-2xl text-xs text-[#849495] font-['JetBrains_Mono'] flex flex-col items-center gap-3">
          <p>No recurring subscriptions detected yet from transaction history.</p>
          <button
            onClick={handleRunDetection}
            className="px-3 py-1.5 rounded-lg bg-[#282a30] hover:bg-[#33353b] text-[#dbfcff]"
          >
            Trigger Ingestion Analysis
          </button>
        </div>
      )}
    </div>
  );
};

