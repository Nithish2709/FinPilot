import { apiClient } from './client';
import { DashboardResponse, AnalyticsResponse } from '../types';

export const dashboardApi = {
  async getDashboard(): Promise<DashboardResponse> {
    return apiClient<DashboardResponse>('/dashboard');
  },

  async getAnalytics(startDate?: string, endDate?: string): Promise<AnalyticsResponse> {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    const qs = params.toString();
    return apiClient<AnalyticsResponse>('/analytics' + (qs ? '?' + qs : ''));
  },
};
