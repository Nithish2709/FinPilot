import React, { useState, useEffect } from 'react';
import { PiggyBank, Target, TrendingUp, ShieldCheck, Sparkles, CheckCircle2, Plus, AlertTriangle, RefreshCw, Trash2 } from 'lucide-react';
import { budgetsApi } from '../api/budgets';
import { goalsApi } from '../api/goals';
import { Budget, Goal } from '../types';
import { useAuth } from '../context/AuthContext';

export const BudgetsGoalsView: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const [budgets, setBudgets] = useState<Budget[]>([]);
  const [goals, setGoals] = useState<Goal[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // New Goal Form
  const [showGoalModal, setShowGoalModal] = useState(false);
  const [goalName, setGoalName] = useState('');
  const [goalTarget, setGoalTarget] = useState(50000);
  const [goalCurrent, setGoalCurrent] = useState(10000);
  const [goalDate, setGoalDate] = useState('2026-12-31');

  // New Budget Form
  const [showBudgetModal, setShowBudgetModal] = useState(false);
  const [budgetName, setBudgetName] = useState('');
  const [budgetCategory, setBudgetCategory] = useState('Food & Dining');
  const [budgetAmount, setBudgetAmount] = useState(15000);

  const fetchData = async () => {
    if (!isAuthenticated) return;
    setLoading(true);
    setError(null);
    try {
      const [budgetsRes, goalsRes] = await Promise.all([
        budgetsApi.getBudgets().catch(() => []),
        goalsApi.getGoals().catch(() => []),
      ]);
      setBudgets(budgetsRes);
      setGoals(goalsRes);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch budgets and goals.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [isAuthenticated]);

  const handleCreateGoal = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await goalsApi.createGoal({
        name: goalName,
        target_amount: Number(goalTarget),
        current_amount: Number(goalCurrent),
        target_date: goalDate || null,
      });
      setShowGoalModal(false);
      setGoalName('');
      fetchData();
    } catch (err: any) {
      alert(err.message || 'Failed to create goal');
    }
  };

  const handleCreateBudget = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await budgetsApi.createBudget({
        name: budgetName,
        category: budgetCategory,
        amount: Number(budgetAmount),
        start_date: new Date().toISOString().split('T')[0],
      });
      setShowBudgetModal(false);
      setBudgetName('');
      fetchData();
    } catch (err: any) {
      alert(err.message || 'Failed to create budget');
    }
  };

  const handleDeleteBudget = async (id: string) => {
    if (!confirm('Are you sure you want to delete this budget?')) return;
    await budgetsApi.deleteBudget(id);
    fetchData();
  };

  const handleDeleteGoal = async (id: string) => {
    if (!confirm('Are you sure you want to delete this goal?')) return;
    await goalsApi.deleteGoal(id);
    fetchData();
  };

  const totalGoalAssets = goals.reduce((acc, g) => acc + Number(g.target_amount), 0);

  return (
    <div className="flex flex-col gap-6 w-full max-w-7xl mx-auto pb-24">
      {/* Header Banner */}
      <div className="flex flex-wrap items-center justify-between gap-3 pt-2">
        <div className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-[#00f0ff] animate-pulse"></span>
          <span className="font-['JetBrains_Mono'] text-[11px] text-[#00f0ff] tracking-widest font-semibold uppercase">
            STAGE 4 & STAGE 9 // LIVE BUDGETS & GOALS ENGINE
          </span>
        </div>
        <div className="flex items-center gap-2 font-['JetBrains_Mono'] text-xs text-[#849495]">
          <span>TOTAL TARGET ASSETS: <span className="text-[#00e296] font-bold">₹{totalGoalAssets.toLocaleString('en-IN')}</span></span>
        </div>
      </div>

      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-col gap-1">
          <h1 className="font-['Plus_Jakarta_Sans'] text-2xl md:text-3xl font-bold text-[#dbfcff] tracking-tight">
            Budgets, Reserves & Goal Vectors
          </h1>
          <p className="text-sm text-[#b9cacb]">
            Authoritative backend calculations for progress, spending limits, and required monthly savings.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowBudgetModal(true)}
            className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-[#191c21] hover:bg-[#282a30] text-[#dbfcff] border border-white/10 text-xs font-semibold font-['JetBrains_Mono'] transition-all"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>+ Create Budget</span>
          </button>

          <button
            onClick={() => setShowGoalModal(true)}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-gradient-to-r from-[#0068ed] to-[#00f0ff] text-[#002d6e] hover:brightness-110 text-xs font-bold font-['JetBrains_Mono'] transition-all shadow-[0_0_15px_rgba(0,240,255,0.4)]"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>+ New Goal Vector</span>
          </button>
        </div>
      </div>

      {error && (
        <div className="p-3 rounded-xl bg-[#93000a]/20 border border-[#ffb4ab]/40 text-[#ffb4ab] text-xs flex items-center gap-2">
          <AlertTriangle className="w-4 h-4" />
          <span>{error}</span>
        </div>
      )}

      {/* SECTION 1: GOALS */}
      <div className="flex flex-col gap-3">
        <div className="flex items-center justify-between">
          <h2 className="font-['Plus_Jakarta_Sans'] text-lg font-bold text-[#dbfcff] flex items-center gap-2">
            <Target className="w-5 h-5 text-[#00e296]" />
            <span>Savings Goals ({goals.length})</span>
          </h2>
        </div>

        {goals.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {goals.map((g) => {
              const current = Number(g.current_amount || 0);
              const target = Number(g.target_amount || 1);
              const percent = g.percentage_complete !== undefined ? Number(g.percentage_complete) : Math.min(100, Math.round((current / target) * 100));

              return (
                <div key={g.id} className="p-5 rounded-2xl bg-[#191c21]/80 backdrop-blur-xl border border-white/5 flex flex-col gap-4 shadow-xl">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      <div className="p-2.5 rounded-xl bg-[#1d2025] text-[#00f0ff]">
                        <PiggyBank className="w-5 h-5" />
                      </div>
                      <div>
                        <h3 className="font-['Plus_Jakarta_Sans'] text-base font-bold text-[#dbfcff]">
                          {g.name}
                        </h3>
                        <span className="font-['JetBrains_Mono'] text-xs text-[#849495]">
                          TARGET DATE: {g.target_date || 'Ongoing'}
                        </span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="font-['JetBrains_Mono'] text-lg font-bold text-[#00e296]">
                        {percent}%
                      </span>
                      <button onClick={() => handleDeleteGoal(g.id)} className="text-[#849495] hover:text-[#ffb4ab] p-1">
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>

                  <div className="flex flex-col gap-1.5">
                    <div className="w-full bg-[#111319] h-2.5 rounded-full overflow-hidden">
                      <div 
                        className="bg-gradient-to-r from-[#0068ed] to-[#00f0ff] h-full rounded-full transition-all duration-500" 
                        style={{ width: `${percent}%` }}
                      ></div>
                    </div>
                    <div className="flex items-center justify-between font-['JetBrains_Mono'] text-xs text-[#849495]">
                      <span>Saved: <strong className="text-[#e2e2ea]">₹{current.toLocaleString('en-IN')}</strong></span>
                      <span>Target: <strong className="text-[#e2e2ea]">₹{target.toLocaleString('en-IN')}</strong></span>
                    </div>
                  </div>

                  <div className="flex items-center justify-between pt-2 border-t border-white/5 text-xs font-['JetBrains_Mono']">
                    <span className="text-[#b9cacb] flex items-center gap-1.5">
                      <Sparkles className="w-3.5 h-3.5 text-[#00dbe9]" />
                      <span>{g.required_monthly_saving ? `Required SIP: ₹${Number(g.required_monthly_saving).toLocaleString('en-IN')}/mo` : 'On track'}</span>
                    </span>
                    <span className="text-[#849495]">Remaining: ₹{Number(g.remaining_amount || (target - current)).toLocaleString('en-IN')}</span>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="p-8 text-center bg-[#191c21]/40 border border-dashed border-white/10 rounded-2xl text-xs text-[#849495] font-['JetBrains_Mono']">
            No goals created yet. Click "+ New Goal Vector" to plan a reserve or sinking fund.
          </div>
        )}
      </div>

      {/* SECTION 2: BUDGETS */}
      <div className="flex flex-col gap-3 pt-4 border-t border-white/5">
        <div className="flex items-center justify-between">
          <h2 className="font-['Plus_Jakarta_Sans'] text-lg font-bold text-[#dbfcff] flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-[#b0c6ff]" />
            <span>Category Budgets ({budgets.length})</span>
          </h2>
        </div>

        {budgets.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {budgets.map((b) => {
              const spent = Number(b.spent_amount || 0);
              const limit = Number(b.amount || 1);
              const percent = b.percentage_used !== undefined ? Number(b.percentage_used) : Math.min(100, Math.round((spent / limit) * 100));
              const status = b.status || (spent > limit ? 'OVER_BUDGET' : spent > limit * 0.8 ? 'NEAR_LIMIT' : 'ON_TRACK');

              const statusColor = 
                status === 'OVER_BUDGET' ? 'bg-[#93000a]/40 text-[#ffb4ab] border-[#ffb4ab]/30' :
                status === 'NEAR_LIMIT' ? 'bg-[#b0c6ff]/15 text-[#b0c6ff] border-[#b0c6ff]/30' :
                'bg-[#00e296]/15 text-[#00e296] border-[#00e296]/30';

              return (
                <div key={b.id} className="p-4 rounded-2xl bg-[#191c21]/80 border border-white/5 flex flex-col gap-3 shadow-md">
                  <div className="flex items-start justify-between">
                    <div>
                      <span className="font-['JetBrains_Mono'] text-[10px] text-[#849495] uppercase font-semibold">
                        {b.category}
                      </span>
                      <h4 className="font-['Plus_Jakarta_Sans'] text-sm font-bold text-[#dbfcff]">
                        {b.name}
                      </h4>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={`px-2 py-0.5 rounded font-['JetBrains_Mono'] text-[10px] font-bold border ${statusColor}`}>
                        {status}
                      </span>
                      <button onClick={() => handleDeleteBudget(b.id)} className="text-[#849495] hover:text-[#ffb4ab]">
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>

                  <div className="flex flex-col gap-1">
                    <div className="w-full bg-[#111319] h-2 rounded-full overflow-hidden">
                      <div 
                        className={`h-full rounded-full ${status === 'OVER_BUDGET' ? 'bg-[#ffb4ab]' : 'bg-[#00f0ff]'}`} 
                        style={{ width: `${Math.min(100, percent)}%` }}
                      ></div>
                    </div>
                    <div className="flex items-center justify-between font-['JetBrains_Mono'] text-[11px] text-[#849495]">
                      <span>Spent: ₹{spent.toLocaleString('en-IN')}</span>
                      <span>Limit: ₹{limit.toLocaleString('en-IN')}</span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="p-8 text-center bg-[#191c21]/40 border border-dashed border-white/10 rounded-2xl text-xs text-[#849495] font-['JetBrains_Mono']">
            No budgets configured yet. Click "+ Create Budget" to set category spending thresholds.
          </div>
        )}
      </div>

      {/* Goal Modal */}
      {showGoalModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
          <form onSubmit={handleCreateGoal} className="w-full max-w-md bg-[#111319] border border-white/10 rounded-2xl p-6 flex flex-col gap-4 shadow-2xl">
            <h3 className="font-['Plus_Jakarta_Sans'] text-base font-bold text-[#dbfcff]">Create Financial Goal</h3>
            <input
              type="text"
              required
              placeholder="Goal Name (e.g. 6-Month Emergency Runway)"
              value={goalName}
              onChange={(e) => setGoalName(e.target.value)}
              className="bg-[#191c21] text-xs p-2.5 rounded-xl border border-white/10 text-[#e2e2ea]"
            />
            <input
              type="number"
              required
              placeholder="Target Amount (₹)"
              value={goalTarget}
              onChange={(e) => setGoalTarget(Number(e.target.value))}
              className="bg-[#191c21] text-xs p-2.5 rounded-xl border border-white/10 text-[#e2e2ea]"
            />
            <input
              type="number"
              placeholder="Current Saved (₹)"
              value={goalCurrent}
              onChange={(e) => setGoalCurrent(Number(e.target.value))}
              className="bg-[#191c21] text-xs p-2.5 rounded-xl border border-white/10 text-[#e2e2ea]"
            />
            <input
              type="date"
              value={goalDate}
              onChange={(e) => setGoalDate(e.target.value)}
              className="bg-[#191c21] text-xs p-2.5 rounded-xl border border-white/10 text-[#e2e2ea]"
            />
            <div className="flex items-center justify-end gap-2 pt-2">
              <button type="button" onClick={() => setShowGoalModal(false)} className="px-3 py-1.5 text-xs text-[#849495]">Cancel</button>
              <button type="submit" className="px-4 py-1.5 bg-[#00f0ff] text-[#002d6e] text-xs font-bold rounded-lg">Save Goal</button>
            </div>
          </form>
        </div>
      )}

      {/* Budget Modal */}
      {showBudgetModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
          <form onSubmit={handleCreateBudget} className="w-full max-w-md bg-[#111319] border border-white/10 rounded-2xl p-6 flex flex-col gap-4 shadow-2xl">
            <h3 className="font-['Plus_Jakarta_Sans'] text-base font-bold text-[#dbfcff]">Create Category Budget</h3>
            <input
              type="text"
              required
              placeholder="Budget Name (e.g. Monthly Grocery Cap)"
              value={budgetName}
              onChange={(e) => setBudgetName(e.target.value)}
              className="bg-[#191c21] text-xs p-2.5 rounded-xl border border-white/10 text-[#e2e2ea]"
            />
            <input
              type="text"
              required
              placeholder="Category (e.g. Food & Dining, Utilities)"
              value={budgetCategory}
              onChange={(e) => setBudgetCategory(e.target.value)}
              className="bg-[#191c21] text-xs p-2.5 rounded-xl border border-white/10 text-[#e2e2ea]"
            />
            <input
              type="number"
              required
              placeholder="Monthly Limit (₹)"
              value={budgetAmount}
              onChange={(e) => setBudgetAmount(Number(e.target.value))}
              className="bg-[#191c21] text-xs p-2.5 rounded-xl border border-white/10 text-[#e2e2ea]"
            />
            <div className="flex items-center justify-end gap-2 pt-2">
              <button type="button" onClick={() => setShowBudgetModal(false)} className="px-3 py-1.5 text-xs text-[#849495]">Cancel</button>
              <button type="submit" className="px-4 py-1.5 bg-[#00f0ff] text-[#002d6e] text-xs font-bold rounded-lg">Save Budget</button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};

