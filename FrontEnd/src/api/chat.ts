import { apiClient } from './client';
import { Conversation, Message } from '../types';

export interface MessageListResponse {
  items: Message[];
  total: number;
  limit: number;
  offset: number;
}

export interface ConversationListResponse {
  items: Conversation[];
  total: number;
  limit: number;
  offset: number;
}

export const chatApi = {
  async getConversations(limit = 20, offset = 0): Promise<ConversationListResponse> {
    return apiClient<ConversationListResponse>('/conversations?limit=' + limit + '&offset=' + offset);
  },

  async createConversation(title?: string): Promise<Conversation> {
    return apiClient<Conversation>('/conversations', {
      method: 'POST',
      body: JSON.stringify({ title: title || 'Financial Consultation' }),
    });
  },

  async getConversation(id: string): Promise<Conversation> {
    return apiClient<Conversation>('/conversations/' + id);
  },

  async deleteConversation(id: string): Promise<void> {
    return apiClient<void>('/conversations/' + id, {
      method: 'DELETE',
    });
  },

  async getMessages(conversationId: string, limit = 50, offset = 0): Promise<MessageListResponse> {
    return apiClient<MessageListResponse>(
      '/conversations/' + conversationId + '/messages?limit=' + limit + '&offset=' + offset
    );
  },

  async sendMessage(conversationId: string, content: string): Promise<Message> {
    return apiClient<Message>('/conversations/' + conversationId + '/messages', {
      method: 'POST',
      body: JSON.stringify({ content }),
    });
  },
};
