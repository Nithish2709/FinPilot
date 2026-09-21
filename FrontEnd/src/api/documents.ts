import { apiClient } from './client';
import { DocumentRecord, DocumentSearchResponse, TransactionRecord } from '../types';

export interface TransactionListResponse {
  items: TransactionRecord[];
  total: number;
  limit: number;
  offset: number;
}

export const documentsApi = {
  async uploadDocument(file: File): Promise<DocumentRecord> {
    const formData = new FormData();
    formData.append('file', file);

    return apiClient<DocumentRecord>('/documents/upload', {
      method: 'POST',
      body: formData,
    });
  },

  async getDocuments(limit = 20, offset = 0): Promise<DocumentRecord[]> {
    return apiClient<DocumentRecord[]>('/documents?limit=' + limit + '&offset=' + offset);
  },

  async getDocument(id: string): Promise<DocumentRecord> {
    return apiClient<DocumentRecord>('/documents/' + id);
  },

  async searchDocuments(query: string, topK = 5): Promise<DocumentSearchResponse> {
    return apiClient<DocumentSearchResponse>('/documents/search', {
      method: 'POST',
      body: JSON.stringify({ query, top_k: topK }),
    });
  },

  async getTransactions(limit = 50, offset = 0, category?: string): Promise<TransactionListResponse> {
    const params = new URLSearchParams({ limit: String(limit), offset: String(offset) });
    if (category && category !== 'all') {
      params.append('category', category);
    }
    return apiClient<TransactionListResponse>('/transactions?' + params.toString());
  },
};
