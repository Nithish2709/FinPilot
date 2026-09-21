import { apiClient } from './client';
import { Budget } from '../types';

export interface BudgetCreatePayload {
  name: string;
  category: string;
  amount: number;
  period?: string;
  start_date: string;
  end_date?: string | null;
}

export const budgetsApi = {
  async getBudgets(): Promise<Budget[]> {
    return apiClient<Budget[]>('/budgets');
  },

  async createBudget(payload: BudgetCreatePayload): Promise<Budget> {
    return apiClient<Budget>('/budgets', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  async getBudget(id: string): Promise<Budget> {
    return apiClient<Budget>('/budgets/' + id);
  },

  async updateBudget(id: string, payload: Partial<BudgetCreatePayload>): Promise<Budget> {
    return apiClient<Budget>('/budgets/' + id, {
      method: 'PUT',
      body: JSON.stringify(payload),
    });
  },

  async deleteBudget(id: string): Promise<void> {
    return apiClient<void>('/budgets/' + id, {
      method: 'DELETE',
    });
  },
};
