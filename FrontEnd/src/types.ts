export type ViewMode = 
  | 'command-center'
  | 'ai-assistant'
  | 'scenario-engine'
  | 'subscriptions'
  | 'budgets-goals'
  | 'financial-documents';

export interface TelemetryMetric {
  title: string;
  amount: string;
  subtext: string;
  trend?: string;
  badge?: string;
  type?: 'positive' | 'neutral' | 'warning' | 'critical';
}

export interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  timestamp: string;
  queryType?: string;
  content: string;
  scenarioData?: {
    totalLiquid: number;
    committed: number;
    proposed: number;
    immediateBuffer: number;
    recommendedDate: string;
    optionABuffer: number;
    optionBBuffer: number;
  };
}

export interface ScenarioSimulationParams {
  assetName: string;
  amount: number;
  plannedDate: string;
  category: string;
  protocol: 'cash' | 'emi-3m' | 'wait-inflow';
}

export interface TransactionRecord {
  id: string;
  merchant: string;
  category: string;
  amount: number;
  date: string;
  account: string;
  isRecurring?: boolean;
  anomaly?: boolean;
}

export interface RecurringCommitment {
  id: string;
  name: string;
  cost: number;
  renewsIn: string;
  notes: string;
  flagged?: boolean;
  category: string;
}

export interface ReserveVault {
  id: string;
  name: string;
  current: number;
  target: number;
  targetDate: string;
  percent: number;
}
