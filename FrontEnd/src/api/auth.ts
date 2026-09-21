import { apiClient, setAuthTokens } from './client';
import { User, TokenResponse } from '../types';

export interface RegisterPayload {
  email: string;
  password: string;
  name: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export const authApi = {
  async register(payload: RegisterPayload): Promise<User> {
    return apiClient<User>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  async login(payload: LoginPayload): Promise<TokenResponse> {
    const data = await apiClient<TokenResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
    setAuthTokens(data.access_token, data.refresh_token);
    return data;
  },

  async getMe(): Promise<User> {
    return apiClient<User>('/auth/me');
  },

  async logout(): Promise<void> {
    try {
      await apiClient('/auth/logout', { method: 'POST' });
    } catch {
      // Ignore network errors on logout
    } finally {
      setAuthTokens(null, null);
    }
  },
};
