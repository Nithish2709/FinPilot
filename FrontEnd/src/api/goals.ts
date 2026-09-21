import { apiClient } from './client';
import { Goal } from '../types';

export interface GoalCreatePayload {
  name: string;
  target_amount: number;
  current_amount?: number;
  target_date?: string | null;
}

export const goalsApi = {
  async getGoals(): Promise<Goal[]> {
    return apiClient<Goal[]>('/goals');
  },

  async createGoal(payload: GoalCreatePayload): Promise<Goal> {
    return apiClient<Goal>('/goals', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  async getGoal(id: string): Promise<Goal> {
    return apiClient<Goal>('/goals/' + id);
  },

  async updateGoal(id: string, payload: Partial<GoalCreatePayload>): Promise<Goal> {
    return apiClient<Goal>('/goals/' + id, {
      method: 'PUT',
      body: JSON.stringify(payload),
    });
  },

  async deleteGoal(id: string): Promise<void> {
    return apiClient<void>('/goals/' + id, {
      method: 'DELETE',
    });
  },
};
