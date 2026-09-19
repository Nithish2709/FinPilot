import React, { useState } from 'react';
import { X, Copy, Check, Terminal, Sparkles, Layers, Palette, Cpu } from 'lucide-react';

interface PromptModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const PromptModal: React.FC<PromptModalProps> = ({ isOpen, onClose }) => {
  const [copied, setCopied] = useState(false);

  if (!isOpen) return null;

  const antigravityPrompt = `Build "FinPilot — Autonomous Financial Intelligence & Decision Engine", a high-density, real-time financial telemetry dashboard and deterministic scenario simulator built in React (or React Native for Web) styled with Tailwind CSS and Lucide icons.

### 1. Visual Aesthetics & Design System (Dark Tactical FinTech)
- Tone: High-precision terminal meets modern cyber-executive financial cockpit. Dark background (#0c0e13, #111319, #191c21), luminous accents (Primary: #00f0ff electric cyan, Secondary: #0068ed cobalt blue, Tertiary/Success: #00e296 emerald, Alert: #ffb4ab / #93000a crimson).
- Typography: 'Plus Jakarta Sans' for primary headings, 'Inter' for body, and 'JetBrains Mono' for numbers, currency (₹), telemetry timestamps, and tags.
- Crisp border highlights: 1px subtle borders (rgba(255,255,255,0.06)), backdrop blur filters, and soft cyan glows on active elements.
- Icons: Strict use of 'lucide-react' (Bot, LayoutGrid, GitBranch, Calendar, PiggyBank, FileText, PlusCircle, ShieldCheck, AlertTriangle, Sliders, Laptop, CreditCard, Building2, TrendingUp, TrendingDown, ArrowDownLeft, ArrowUpRight, Search, Bell, Settings, etc.).

### 2. Information Architecture & Navigation
- Fixed Left Sidebar (256px width):
  - Brand Header: FinPilot logo (glowing circular compass emblem) + "AI DECISION ENGINE" status badge.
  - "+ New Analysis / Chat" action button with cyan hover border.
  - Workspace Matrix: AI Assistant, Command Center, Scenario Engine (Buy/Wait), Subscriptions & Commitments, Budgets & Goals, Financial Documents.
  - Neural Memory: Indexed history grouped by Today, Yesterday, Previous 7 Days.
  - Telemetry Footer: Pulsing green indicator with "SYNAPSE V4.2 ONLINE".
- Header Bar:
  - Global omni-search input ("Search financial memory, transactions, scenarios...").
  - Status Badges: RUNWAY 4.8 MO, COMMITTED 34%, CORE CONFIDENCE 99.8%.
  - User Avatar with live online ring, Settings & Notifications.

### 3. Core Modules & Screen Implementation
1. Command Center (Flight Path & Health):
   - 5 High-Density Metric Cards: Net Liquid Assets (₹3,42,850 + sparkline), Monthly Inflow (₹1,25,000), Monthly Outflow (₹68,400, Burn 54.7%), Committed Load (₹32,000), Discretionary Safe Buffer (₹24,600, ₹820/day).
   - 90-Day Cash Flow & Runway Projection: Interactive SVG trajectory curve with milestone event flags (Rent 5th Sep ₹18k, AWS 12th Sep ₹4.5k, Tax reserve, etc.).
   - Neural Drift & Pattern Evidence: AI detection of +23% food delivery increase vs July baseline with dynamic comparison bars and "Set Food Cap" mitigation button.
   - Categorical Outflow Ring: Donut chart breakdown (Housing 38%, Food 18%, Tech 14%, Discretionary 12%, Transport 9%, Sinking Fund 9%).
   - Recurring Commitments Radar & Reserves Vaults with progress bars.
   - Sticky Bottom Autonomous Dispatch Banner with 3 proactive recommendations and "Simulate Impact" / "Execute" buttons.

2. AI Assistant (Conversational Decision Engine):
   - System Banner: FINPILOT NEURAL ENGINE v3.4, AES-256 E2E, 120-Day Context Cache.
   - 6 Quick Prompts (Where did money go, Show recurring payments, Can I buy a ₹60,000 laptop, etc.).
   - Audited Chat Dialogue Stream:
     - User query: "Can I buy a ₹60,000 laptop?"
     - FinPilot AI Response: Scenario analysis header, 4-col financial status cards (Liquid Cash, Committed, Proposed, Immediate Buffer), 60-day cash depletion SVG curve with critical dip.
     - Dual comparison: Option A (Buy Today, 3.5% critical buffer) vs Option B (Purchase on Sept 1st post-payroll, ₹63,000 buffer, Recommended).
     - Interactive Dynamic Purchase Cost Slider (₹40,000 to ₹90,000) that recomputes immediate buffer, Sept 1 buffer, and safety threshold in real time!
     - Ingest Queue strip + persistent bottom chat console with file attachment & voice dictation stubs.

3. Scenario Engine (Buy/Wait Stress-Testing):
   - Telemetry parameters console: Target asset, impact amount, planned date, protocol tabs (Direct Cash, 3M No-Cost EMI, Wait for Inflow).
   - Scenario Alpha vs Beta cards with circular SVG gauges (3.5% vs 98% confidence) and waterfall ledger breakdowns.
   - Dynamic Trajectory Matrix comparing balance vector paths across critical ₹20k threshold.

4. Financial Documents & Ledger Ingestion:
   - 5 Telemetry cards: 184 transactions, 14 commitments, 2 accounts synced, 99.2% hygiene.
   - Drag-and-drop statement dropzone with instant client-side OCR & extraction feedback.
   - Neural ledger pipeline steps + live parsed transactions table with filter & search.

5. Subscriptions & Budgets/Goals:
   - Zombie subscription detection (+₹2,719 saved purge action) and multi-goal capital vaults with animated progress bars.`;

  const handleCopy = () => {
    navigator.clipboard.writeText(antigravityPrompt);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-md z-50 flex items-center justify-center p-4">
      <div className="relative w-full max-w-4xl max-h-[90vh] bg-[#111319] border border-[#00f0ff]/40 rounded-2xl shadow-[0_0_50px_rgba(0,240,255,0.2)] flex flex-col overflow-hidden">
        {/* Modal Header */}
        <div className="p-4 md:p-6 bg-[#191c21] border-b border-white/5 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-[#00f0ff]/10 text-[#00f0ff]">
              <Terminal className="w-5 h-5" />
            </div>
            <div>
              <h2 className="font-['Plus_Jakarta_Sans'] text-lg font-bold text-[#dbfcff]">
                Antigravity Production Prompt
              </h2>
              <p className="font-['JetBrains_Mono'] text-xs text-[#849495]">
                Tailored for Antigravity AI builder • React + Tailwind CSS + Lucide Icons
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleCopy}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-gradient-to-r from-[#0068ed] to-[#00f0ff] text-[#002d6e] hover:brightness-110 font-['JetBrains_Mono'] text-xs font-bold transition-all shadow-md"
            >
              {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
              <span>{copied ? 'Copied Prompt!' : 'Copy Prompt'}</span>
            </button>

            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-[#849495] hover:text-[#e2e2ea] hover:bg-[#282a30] transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Modal Body with code view */}
        <div className="p-4 md:p-6 overflow-y-auto flex-1 font-['JetBrains_Mono'] text-xs leading-relaxed text-[#b9cacb] bg-[#0c0e13]">
          <pre className="whitespace-pre-wrap font-mono select-all bg-[#111319] p-4 rounded-xl border border-white/5 text-[#dbfcff]">
            {antigravityPrompt}
          </pre>
        </div>

        {/* Modal Footer */}
        <div className="p-3.5 bg-[#191c21] border-t border-white/5 flex items-center justify-between text-xs font-['JetBrains_Mono'] text-[#849495]">
          <span>Prompt optimized with exact color tokens, SVG trajectory vectors, and live slider reactivity.</span>
          <button
            onClick={onClose}
            className="px-3 py-1 rounded bg-[#282a30] text-[#e2e2ea] hover:bg-[#33353b] transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
