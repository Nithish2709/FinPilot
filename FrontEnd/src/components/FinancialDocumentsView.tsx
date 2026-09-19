import React, { useState } from 'react';
import { 
  FileText, 
  UploadCloud, 
  CheckCircle2, 
  AlertTriangle, 
  Search, 
  Filter, 
  ArrowDownLeft, 
  ArrowUpRight, 
  FileSpreadsheet, 
  Download,
  Sparkles,
  RefreshCw,
  Cpu
} from 'lucide-react';
import { TransactionRecord } from '../types';

export const FinancialDocumentsView: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [filterCategory, setFilterCategory] = useState<string>('all');
  const [uploadStatus, setUploadStatus] = useState<string | null>(null);

  const initialTransactions: TransactionRecord[] = [
    { id: 'TX-9401', merchant: 'Tata Power Energy', category: 'Utilities', amount: 3420, date: '18 Aug, 2025', account: 'HDFC Salary ••4920' },
    { id: 'TX-9402', merchant: 'Swiggy Gourmet Delivery', category: 'Food & Dining', amount: 1426, date: '17 Aug, 2025', account: 'ICICI Credit ••8812', anomaly: true },
    { id: 'TX-9403', merchant: 'Cult.Fit Annual Gym', category: 'Health & Fitness', amount: 2500, date: '16 Aug, 2025', account: 'HDFC Auto-Debit', isRecurring: true },
    { id: 'TX-9404', merchant: 'Amazon Web Services Inc', category: 'Cloud & Tech', amount: 4520, date: '15 Aug, 2025', account: 'ICICI Credit ••8812', anomaly: true },
    { id: 'TX-9405', merchant: 'Blue Tokai Coffee Roasters', category: 'Food & Dining', amount: 480, date: '14 Aug, 2025', account: 'UPI ••9912' },
    { id: 'TX-9406', merchant: 'Netflix Subscription', category: 'Entertainment', amount: 649, date: '12 Aug, 2025', account: 'ICICI Credit ••8812', isRecurring: true },
    { id: 'TX-9407', merchant: 'Reliance Jio Fiber 1Gbps', category: 'Utilities', amount: 1499, date: '10 Aug, 2025', account: 'HDFC Salary ••4920', isRecurring: true },
    { id: 'TX-9408', merchant: 'Apex Consulting Retainer', category: 'Inflow / Revenue', amount: -35000, date: '05 Aug, 2025', account: 'HDFC Salary ••4920' },
  ];

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const fileName = e.target.files[0].name;
      setUploadStatus(`Parsing "${fileName}" via OCR & Neural Tokenizer...`);
      setTimeout(() => {
        setUploadStatus(`Successfully extracted 42 transactions from "${fileName}". Ledger reconciled!`);
      }, 1500);
    }
  };

  const filtered = initialTransactions.filter((tx) => {
    const matchesSearch = tx.merchant.toLowerCase().includes(searchQuery.toLowerCase()) || tx.category.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = filterCategory === 'all' || tx.category.toLowerCase().includes(filterCategory.toLowerCase());
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="flex flex-col gap-6 w-full max-w-7xl mx-auto pb-24">
      {/* Header Banner */}
      <div className="flex flex-wrap items-center justify-between gap-3 pt-2">
        <div className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-[#00f0ff] animate-pulse"></span>
          <span className="font-['JetBrains_Mono'] text-[11px] text-[#00f0ff] tracking-widest font-semibold uppercase">
            DATA INGESTION — LIVE DOCUMENT INTELLIGENCE
          </span>
        </div>
        <div className="flex items-center gap-2 font-['JetBrains_Mono'] text-xs text-[#849495]">
          <span>ZERO DATA RETENTION</span>
          <span>•</span>
          <span className="text-[#00e296]">OCR TOKENIZER V2.8 ACTIVE</span>
        </div>
      </div>

      <div className="flex flex-col gap-1">
        <h1 className="font-['Plus_Jakarta_Sans'] text-2xl md:text-3xl font-bold text-[#dbfcff] tracking-tight">
          Financial Documents & Ingestion Pipeline
        </h1>
        <p className="text-sm text-[#b9cacb]">
          Autonomous multi-format ledger ingestion, OCR extraction, anomaly detection, and double-entry transaction reconciliations.
        </p>
      </div>

      {/* Telemetry Preview Bar (5 Stats) */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
        <div className="p-3.5 rounded-xl bg-[#191c21]/80 border border-white/5 flex flex-col">
          <span className="font-['JetBrains_Mono'] text-[10px] text-[#849495] uppercase font-semibold">Transactions</span>
          <span className="font-['JetBrains_Mono'] text-xl font-bold text-[#e2e2ea]">184</span>
          <span className="text-[11px] text-[#00e296] mt-0.5">Index Verified</span>
        </div>

        <div className="p-3.5 rounded-xl bg-[#191c21]/80 border border-white/5 flex flex-col">
          <span className="font-['JetBrains_Mono'] text-[10px] text-[#849495] uppercase font-semibold">Commitments</span>
          <span className="font-['JetBrains_Mono'] text-xl font-bold text-[#b0c6ff]">14</span>
          <span className="text-[11px] text-[#849495] mt-0.5">Auto-Mapped</span>
        </div>

        <div className="p-3.5 rounded-xl bg-[#191c21]/80 border border-white/5 flex flex-col">
          <span className="font-['JetBrains_Mono'] text-[10px] text-[#849495] uppercase font-semibold">Accounts Synced</span>
          <span className="font-['JetBrains_Mono'] text-xl font-bold text-[#00f0ff]">2</span>
          <span className="text-[11px] text-[#00f0ff] mt-0.5">HDFC + ICICI Live</span>
        </div>

        <div className="p-3.5 rounded-xl bg-[#191c21]/80 border border-white/5 flex flex-col">
          <span className="font-['JetBrains_Mono'] text-[10px] text-[#849495] uppercase font-semibold">Data Hygiene</span>
          <span className="font-['JetBrains_Mono'] text-xl font-bold text-[#00e296]">99.2%</span>
          <span className="text-[11px] text-[#00e296] mt-0.5">Grade A+ Integrity</span>
        </div>

        <div className="p-3.5 rounded-xl bg-[#191c21]/80 border border-white/5 flex flex-col">
          <span className="font-['JetBrains_Mono'] text-[10px] text-[#ffb4ab] uppercase font-semibold">Leaks & Notices</span>
          <span className="font-['JetBrains_Mono'] text-xl font-bold text-[#ffb4ab]">2 Flagged</span>
          <span className="text-[11px] text-[#ffb4ab] mt-0.5">AWS & Swiggy Spikes</span>
        </div>
      </div>

      {/* Drag & Drop Upload Zone */}
      <div className="p-8 rounded-2xl bg-[#191c21]/80 backdrop-blur-xl border-2 border-dashed border-[#00f0ff]/30 hover:border-[#00f0ff] transition-all flex flex-col items-center justify-center text-center gap-3 relative cursor-pointer group">
        <input
          type="file"
          accept=".pdf,.csv,.xlsx,.tsv"
          onChange={handleFileUpload}
          className="absolute inset-0 opacity-0 cursor-pointer w-full h-full"
        />
        <div className="w-14 h-14 rounded-2xl bg-[#1d2025] border border-white/10 flex items-center justify-center text-[#00f0ff] group-hover:scale-110 transition-transform shadow-[0_0_20px_-5px_rgba(0,240,255,0.4)]">
          <UploadCloud className="w-7 h-7" />
        </div>
        <div>
          <p className="font-['Plus_Jakarta_Sans'] text-base font-bold text-[#dbfcff]">
            Drop bank statement PDF, CSV export, or expense receipt
          </p>
          <p className="text-xs text-[#849495] font-['JetBrains_Mono'] mt-1">
            SUPPORTED: HDFC, ICICI, SBI, AXIS, ZERODHA, AMEX, APPLE CARD CSV/PDF (ENCRYPTED IN-MEMORY)
          </p>
        </div>
        <button className="px-4 py-2 rounded-xl bg-[#00f0ff]/10 hover:bg-[#00f0ff]/20 text-[#00f0ff] border border-[#00f0ff]/40 text-xs font-['JetBrains_Mono'] font-bold">
          Browse Local Files
        </button>

        {uploadStatus && (
          <div className="mt-2 p-2.5 rounded-xl bg-[#00e296]/10 border border-[#00e296]/30 text-xs font-['JetBrains_Mono'] text-[#00e296] flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4" />
            <span>{uploadStatus}</span>
          </div>
        )}
      </div>

      {/* Neural Ledger Ingestion Timeline */}
      <div className="p-5 rounded-2xl bg-[#191c21]/80 backdrop-blur-xl border border-white/5 flex flex-col gap-3 shadow-xl">
        <div className="flex items-center justify-between pb-2 border-b border-white/5">
          <span className="font-['JetBrains_Mono'] text-[10px] text-[#849495] uppercase font-semibold">
            NEURAL LEDGER PIPELINE STATUS
          </span>
          <span className="font-['JetBrains_Mono'] text-[10px] text-[#00e296] flex items-center gap-1">
            <Cpu className="w-3 h-3" /> PIPELINE SYNCHRONIZED
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 pt-1 font-['JetBrains_Mono'] text-xs">
          <div className="p-3 rounded-xl bg-[#111319] border border-white/5 flex items-center gap-2.5">
            <CheckCircle2 className="w-4 h-4 text-[#00e296] shrink-0" />
            <div>
              <p className="font-bold text-[#e2e2ea]">1. Document Upload</p>
              <p className="text-[10px] text-[#849495]">Sanitized & SHA-256 Validated</p>
            </div>
          </div>

          <div className="p-3 rounded-xl bg-[#111319] border border-white/5 flex items-center gap-2.5">
            <CheckCircle2 className="w-4 h-4 text-[#00e296] shrink-0" />
            <div>
              <p className="font-bold text-[#e2e2ea]">2. OCR & Tokenizer</p>
              <p className="text-[10px] text-[#849495]">184 Tables Parsed (100%)</p>
            </div>
          </div>

          <div className="p-3 rounded-xl bg-[#111319] border border-white/5 flex items-center gap-2.5">
            <CheckCircle2 className="w-4 h-4 text-[#00e296] shrink-0" />
            <div>
              <p className="font-bold text-[#e2e2ea]">3. Anomaly Scanner</p>
              <p className="text-[10px] text-[#ffb4ab]">2 Outlier Spikes Flagged</p>
            </div>
          </div>

          <div className="p-3 rounded-xl bg-[#111319] border border-[#00f0ff]/30 flex items-center gap-2.5">
            <RefreshCw className="w-4 h-4 text-[#00f0ff] animate-spin shrink-0" />
            <div>
              <p className="font-bold text-[#00f0ff]">4. Double-Entry Sync</p>
              <p className="text-[10px] text-[#849495]">Reconciled with Cash Runway</p>
            </div>
          </div>
        </div>
      </div>

      {/* Parsed Transactions Stream */}
      <div className="p-5 rounded-2xl bg-[#191c21]/80 backdrop-blur-xl border border-white/5 flex flex-col gap-4 shadow-xl">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <span className="font-['JetBrains_Mono'] text-[10px] text-[#849495] uppercase font-semibold">
              TRANSACTION AUDIT REPOSITORY
            </span>
            <h3 className="font-['Plus_Jakarta_Sans'] text-base font-bold text-[#dbfcff]">
              Live Parsed Transactions Stream
            </h3>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <div className="relative">
              <Search className="absolute left-2.5 top-2.5 w-3.5 h-3.5 text-[#849495]" />
              <input
                type="text"
                placeholder="Filter transactions..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="bg-[#111319] text-xs text-[#e2e2ea] placeholder:text-[#849495] pl-8 pr-3 py-1.5 rounded-lg border border-white/5 focus:border-[#00f0ff] focus:outline-none"
              />
            </div>

            <select
              value={filterCategory}
              onChange={(e) => setFilterCategory(e.target.value)}
              className="bg-[#111319] text-xs text-[#e2e2ea] px-3 py-1.5 rounded-lg border border-white/5 focus:border-[#00f0ff] focus:outline-none font-['JetBrains_Mono']"
            >
              <option value="all">All Categories</option>
              <option value="utilities">Utilities</option>
              <option value="food">Food & Dining</option>
              <option value="cloud">Cloud & Tech</option>
              <option value="entertainment">Entertainment</option>
              <option value="inflow">Inflow / Revenue</option>
            </select>
          </div>
        </div>

        {/* Transactions Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-['JetBrains_Mono']">
            <thead>
              <tr className="border-b border-white/5 text-[#849495] uppercase text-[10px]">
                <th className="py-2.5 px-3">Date</th>
                <th className="py-2.5 px-3">Merchant / Entity</th>
                <th className="py-2.5 px-3">Category</th>
                <th className="py-2.5 px-3">Account</th>
                <th className="py-2.5 px-3">Status</th>
                <th className="py-2.5 px-3 text-right">Amount</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {filtered.map((tx) => (
                <tr key={tx.id} className="hover:bg-[#1d2025]/60 transition-colors">
                  <td className="py-3 px-3 text-[#849495] whitespace-nowrap">{tx.date}</td>
                  <td className="py-3 px-3 font-semibold text-[#e2e2ea] whitespace-nowrap flex items-center gap-2">
                    <span>{tx.merchant}</span>
                    {tx.anomaly && (
                      <span className="px-1.5 py-0.2 rounded bg-[#93000a]/50 text-[#ffb4ab] text-[9px] font-bold">
                        SPIKE
                      </span>
                    )}
                    {tx.isRecurring && (
                      <span className="px-1.5 py-0.2 rounded bg-[#0068ed]/20 text-[#7df4ff] text-[9px]">
                        RECURRING
                      </span>
                    )}
                  </td>
                  <td className="py-3 px-3 text-[#b9cacb] whitespace-nowrap">{tx.category}</td>
                  <td className="py-3 px-3 text-[#849495] whitespace-nowrap">{tx.account}</td>
                  <td className="py-3 px-3 whitespace-nowrap">
                    <span className="flex items-center gap-1 text-[#00e296] text-[10px]">
                      <CheckCircle2 className="w-3 h-3" /> Reconciled
                    </span>
                  </td>
                  <td className={`py-3 px-3 text-right font-bold whitespace-nowrap ${tx.amount < 0 ? 'text-[#00e296]' : 'text-[#e2e2ea]'}`}>
                    {tx.amount < 0 ? `+₹${Math.abs(tx.amount).toLocaleString('en-IN')}` : `₹${tx.amount.toLocaleString('en-IN')}`}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
