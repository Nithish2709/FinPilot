import { apiClient } from './client';
import { PurchaseAnalysisResponse } from '../types';

export interface PurchaseAnalysisRequest {
  amount: number;
  purchase_date?: string;
  description?: string;
  safety_buffer?: number;
}

export const purchasesApi = {
  async analyzePurchase(payload: PurchaseAnalysisRequest): Promise<PurchaseAnalysisResponse> {
    return apiClient<PurchaseAnalysisResponse>('/purchases/analyze', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },
};
