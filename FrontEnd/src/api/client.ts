/**
 * Centralized API client for FinPilot frontend.
 * Enforces:
 * - Dynamic environment base URL (VITE_API_BASE_URL)
 * - Automatic Authorization: Bearer <token> injection
 * - Token refreshing on 401
 * - Standardized error normalization (ApiError)
 */

export interface ApiError {
  status: number;
  message: string;
  details?: any;
}

const BASE_URL = (import.meta.env.VITE_API_BASE_URL || '/api/v1').replace(/\/$/, '');

let accessToken: string | null = localStorage.getItem('finpilot_access_token');
let refreshToken: string | null = localStorage.getItem('finpilot_refresh_token');

export const setAuthTokens = (access: string | null, refresh: string | null) => {
  accessToken = access;
  refreshToken = refresh;
  if (access) {
    localStorage.setItem('finpilot_access_token', access);
  } else {
    localStorage.removeItem('finpilot_access_token');
  }
  if (refresh) {
    localStorage.setItem('finpilot_refresh_token', refresh);
  } else {
    localStorage.removeItem('finpilot_refresh_token');
  }
};

export const getStoredAccessToken = () => accessToken;
export const getStoredRefreshToken = () => refreshToken;

let isRefreshing = false;
let refreshSubscribers: ((token: string) => void)[] = [];

const subscribeTokenRefresh = (cb: (token: string) => void) => {
  refreshSubscribers.push(cb);
};

const onTokenRefreshed = (token: string) => {
  refreshSubscribers.forEach((cb) => cb(token));
  refreshSubscribers = [];
};

export async function apiClient<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : '/' + endpoint;
  const url = BASE_URL + cleanEndpoint;

  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string>),
  };

  // If body is not FormData, default to application/json
  if (!(options.body instanceof FormData) && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json';
  }

  if (accessToken && !headers['Authorization']) {
    headers['Authorization'] = 'Bearer ' + accessToken;
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  // Handle 401 Unauthorized with token refresh if possible
  if (response.status === 401 && refreshToken && !endpoint.includes('/auth/refresh') && !endpoint.includes('/auth/login')) {
    if (!isRefreshing) {
      isRefreshing = true;
      try {
        const refreshResponse = await fetch(BASE_URL + '/auth/refresh', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ refresh_token: refreshToken }),
        });

        if (refreshResponse.ok) {
          const tokenData = await refreshResponse.json();
          setAuthTokens(tokenData.access_token, tokenData.refresh_token || refreshToken);
          isRefreshing = false;
          onTokenRefreshed(tokenData.access_token);
        } else {
          setAuthTokens(null, null);
          isRefreshing = false;
          window.dispatchEvent(new Event('finpilot:unauthorized'));
          throw {
            status: 401,
            message: 'Session expired. Please log in again.',
          } as ApiError;
        }
      } catch (err) {
        setAuthTokens(null, null);
        isRefreshing = false;
        window.dispatchEvent(new Event('finpilot:unauthorized'));
        throw err;
      }
    }

    // Wait for the refreshed token
    return new Promise((resolve, reject) => {
      subscribeTokenRefresh((newToken: string) => {
        headers['Authorization'] = 'Bearer ' + newToken;
        fetch(url, { ...options, headers })
          .then(async (res) => {
            if (!res.ok) {
              const err = await parseError(res);
              reject(err);
            } else {
              const data = res.status === 204 ? ({} as T) : await res.json();
              resolve(data);
            }
          })
          .catch(reject);
      });
    });
  }

  if (!response.ok) {
    const error = await parseError(response);
    throw error;
  }

  if (response.status === 204) {
    return {} as T;
  }

  return response.json();
}

async function parseError(response: Response): Promise<ApiError> {
  let message = 'Request failed with status ' + response.status;
  let details: any = null;

  try {
    const data = await response.json();
    if (typeof data === 'object' && data !== null) {
      message = data.detail || data.message || message;
      details = data;
    }
  } catch {
    message = response.statusText || message;
  }

  return {
    status: response.status,
    message,
    details,
  };
}
