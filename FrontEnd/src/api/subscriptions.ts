import { apiClient } from './client';
import { SubscriptionRecord } from '../types';

export const subscriptionsApi = {
  async getSubscriptions(): Promise<SubscriptionRecord[]> {
    return apiClient<SubscriptionRecord[]>('/subscriptions');
  },

  async detectSubscriptions(): Promise<{ message: string; count: number }> {
    return apiClient<{ message: string; count: number }>('/subscriptions/detect', {
      method: 'POST',
    });
  },
};
