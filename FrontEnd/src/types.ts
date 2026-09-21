export type ViewMode = 
  | 'command-center'
  | 'ai-assistant'
  | 'scenario-engine'
  | 'subscriptions'
  | 'budgets-goals'
  | 'financial-documents';

// -------------------------------------------------------------
// Authentication & User
// -------------------------------------------------------------
export interface User {
  id: string;
  email: string;
  name: string;
  is_active: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

// -------------------------------------------------------------
// Dashboard & Analytics
// -------------------------------------------------------------
export interface CategorySummaryItem {
  category: string;
  amount: number;
  percentage: number;
  transaction_count: number;
}

export interface ObligationItem {
  merchant: string;
  expected_amount: number;
  expected_date: string;
  frequency: string;
  confidence: number;
  label?: string;
}

export interface UnusualSpendingItem {
  category: string;
  current_amount: number;
  historical_average: number;
  difference: number;
  percentage_change: number;
  severity: 'LOW' | 'MEDIUM' | 'HIGH';
  explanation: string;
}

export interface DashboardResponse {
  current_balance: number;
  balance_basis: string;
  monthly_income: number;
  monthly_expenses: number;
  monthly_refunds: number;
  net_cashflow: number;
  transaction_count: number;
  top_categories: CategorySummaryItem[];
  upcoming_obligations: ObligationItem[];
  goal_progress: any[];
  data_quality?: {
    source: string;
    coverage: string;
    note: string;
  };
}

export interface AnalyticsResponse {
  cashflow: {
    start_date?: string;
    end_date?: string;
    total_income: number;
    total_expenses: number;
    total_refunds: number;
    net_cashflow: number;
    transaction_count: number;
  };
  categories: {
    total_expenses: number;
    categories: CategorySummaryItem[];
  };
  recurring: {
    total_monthly_committed: number;
    active_subscriptions_count: number;
    subscriptions: any[];
  };
  obligations: {
    days_ahead: number;
    total_obligations: number;
    obligations: ObligationItem[];
  };
  unusual_spending: {
    has_sufficient_history: boolean;
    historical_months_available: number;
    anomalies: UnusualSpendingItem[];
  };
}

// -------------------------------------------------------------
// Chat & Conversation
// -------------------------------------------------------------
export interface Conversation {
  id: string;
  user_id: string;
  title: string | null;
  archived: boolean;
  created_at: string;
  updated_at: string;
}

export interface MessageMetadata {
  provider?: string;
  model?: string;
  fallback?: boolean;
  fallback_reason?: string;
  latency_ms?: number;
  tokens?: {
    prompt_tokens?: number;
    completion_tokens?: number;
    total_tokens?: number;
  };
  tool_calls?: any[];
  sources?: string[];
  [key: string]: any;
}

export interface Message {
  id: string;
  conversation_id: string;
  role: 'USER' | 'ASSISTANT' | 'SYSTEM' | 'TOOL';
  content: string;
  sequence_number: number;
  model_used?: string | null;
  metadata?: MessageMetadata | null;
  created_at: string;
}

// -------------------------------------------------------------
// Documents & RAG
// -------------------------------------------------------------
export interface DocumentRecord {
  document_id: string;
  filename: string;
  status: 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED';
  total_records: number;
  successful_records: number;
  failed_records: number;
  duplicate_records: number;
  error_message?: string | null;
  created_at?: string;
}

export interface DocumentChunkResult {
  chunk_id: string;
  document_id: string;
  chunk_index: number;
  content: string;
  score: number;
  metadata?: Record<string, any>;
}

export interface DocumentSearchResponse {
  query: string;
  total_results: number;
  results: DocumentChunkResult[];
}

export interface TransactionRecord {
  id: string;
  transaction_date: string;
  description: string;
  amount: number;
  transaction_type: 'DEBIT' | 'CREDIT' | 'TRANSFER';
  category: string;
  reference_number?: string;
}

// -------------------------------------------------------------
// Budgets & Goals
// -------------------------------------------------------------
export interface Budget {
  id: string;
  user_id: string;
  name: string;
  category: string;
  amount: number;
  period: string;
  start_date: string;
  end_date?: string | null;
  is_active: boolean;
  spent_amount?: number;
  remaining_amount?: number;
  percentage_used?: number;
  status?: 'ON_TRACK' | 'NEAR_LIMIT' | 'OVER_BUDGET';
}

export interface Goal {
  id: string;
  user_id: string;
  name: string;
  target_amount: number;
  current_amount: number;
  target_date?: string | null;
  remaining_amount?: number;
  percentage_complete?: number;
  required_monthly_saving?: number | null;
  is_completed?: boolean;
}

// -------------------------------------------------------------
// Recurring Subscriptions
// -------------------------------------------------------------
export interface SubscriptionRecord {
  id: string;
  merchant: string;
  average_amount: number;
  frequency: string;
  last_payment_date: string;
  next_expected_date?: string | null;
  confidence: number;
  status: string;
  created_at: string;
}

// -------------------------------------------------------------
// Purchase Scenario
// -------------------------------------------------------------
export interface PurchaseScenarioDetail {
  projected_balance: number;
  buffer_difference: number;
}

export interface PurchaseAnalysisResponse {
  current_balance: number;
  upcoming_obligations: number;
  purchase_amount: number;
  safety_buffer: number;
  projected_balance: number;
  buffer_difference: number;
  scenarios: Record<string, PurchaseScenarioDetail>;
  disclaimer: string;
}

