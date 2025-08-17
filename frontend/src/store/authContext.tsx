'use client';

import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
import { AuthState, AuthEvent, AuthContextType, AuthUser } from '@/types/auth';
import { authService } from '@/lib/auth/authService';

// Token storage helper
const TOKEN_KEY = 'auth_token';
const REFRESH_TOKEN_KEY = 'refresh_token';
const USER_KEY = 'auth_user';

class AuthStorage {
  static setToken(token: string): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem(TOKEN_KEY, token);
    }
  }

  static getToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem(TOKEN_KEY);
    }
    return null;
  }

  static setRefreshToken(token: string): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem(REFRESH_TOKEN_KEY, token);
    }
  }

  static getRefreshToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem(REFRESH_TOKEN_KEY);
    }
    return null;
  }

  static setUser(user: AuthUser): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem(USER_KEY, JSON.stringify(user));
    }
  }

  static getUser(): AuthUser | null {
    if (typeof window !== 'undefined') {
      const userStr = localStorage.getItem(USER_KEY);
      return userStr ? JSON.parse(userStr) : null;
    }
    return null;
  }

  static clear(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(REFRESH_TOKEN_KEY);
      localStorage.removeItem(USER_KEY);
    }
  }
}

// Initial state
const initialState: AuthState = {
  user: null,
  token: null,
  refreshToken: null,
  isAuthenticated: false,
  isLoading: true,
  error: null,
};

// Auth reducer
function authReducer(state: AuthState, event: AuthEvent): AuthState {
  switch (event.type) {
    case 'LOGIN_START':
      return {
        ...state,
        isLoading: true,
        error: null,
      };

    case 'LOGIN_SUCCESS':
      return {
        ...state,
        user: event.payload.user,
        token: event.payload.token,
        refreshToken: event.payload.refreshToken,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      };

    case 'LOGIN_ERROR':
      return {
        ...state,
        user: null,
        token: null,
        refreshToken: null,
        isAuthenticated: false,
        isLoading: false,
        error: event.payload,
      };

    case 'LOGOUT':
      return {
        ...state,
        user: null,
        token: null,
        refreshToken: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
      };

    case 'TOKEN_REFRESH':
      return {
        ...state,
        isLoading: false,
        error: null,
      };

    case 'AUTH_ERROR':
      return {
        ...state,
        isLoading: false,
        error: event.payload,
      };

    default:
      return state;
  }
}

// Context
const AuthContext = createContext<AuthContextType | null>(null);

// Provider props
interface AuthProviderProps {
  children: ReactNode;
}

// Auth Provider
export function AuthProvider({ children }: AuthProviderProps) {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Initialize auth state from storage
  useEffect(() => {
    const initAuth = async () => {
      try {
        const token = AuthStorage.getToken();
        const refreshToken = AuthStorage.getRefreshToken();
        const user = AuthStorage.getUser();

        if (token && user) {
          // Verify token by getting current user
          try {
            const currentUser = await authService.getCurrentUser();
            dispatch({
              type: 'LOGIN_SUCCESS',
              payload: {
                user: currentUser,
                token,
                refreshToken: refreshToken || '',
              },
            });
          } catch (error) {
            // Token is invalid, try to refresh
            if (refreshToken) {
              try {
                const response = await authService.refreshToken(refreshToken);
                AuthStorage.setToken(response.data.token);
                AuthStorage.setRefreshToken(response.data.refreshToken);
                AuthStorage.setUser(response.data.user);
                
                dispatch({
                  type: 'LOGIN_SUCCESS',
                  payload: {
                    user: response.data.user,
                    token: response.data.token,
                    refreshToken: response.data.refreshToken,
                  },
                });
              } catch (refreshError) {
                // Refresh failed, clear storage
                AuthStorage.clear();
                dispatch({ type: 'LOGOUT' });
              }
            } else {
              // No refresh token, clear storage
              AuthStorage.clear();
              dispatch({ type: 'LOGOUT' });
            }
          }
        } else {
          dispatch({ type: 'LOGOUT' });
        }
      } catch (error) {
        console.error('Auth initialization error:', error);
        dispatch({ type: 'LOGOUT' });
      }
    };

    initAuth();
  }, []);

  const login = async (credentials: { email: string; password: string; rememberMe?: boolean }) => {
    dispatch({ type: 'LOGIN_START' });
    
    try {
      console.log('AuthContext: Attempting login with credentials', { email: credentials.email });
      const response = await authService.login(credentials);
      console.log('AuthContext: Login successful', response);
      
      // Store tokens and user data
      AuthStorage.setToken(response.data.token);
      AuthStorage.setRefreshToken(response.data.refreshToken);
      AuthStorage.setUser(response.data.user);

      dispatch({
        type: 'LOGIN_SUCCESS',
        payload: {
          user: response.data.user,
          token: response.data.token,
          refreshToken: response.data.refreshToken,
        },
      });
    } catch (error: any) {
      console.error('AuthContext: Login failed', error);
      
      let errorMessage = 'Login failed';
      
      if (error.message) {
        errorMessage = error.message;
      } else if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.response?.data?.message) {
        errorMessage = error.response.data.message;
      } else if (error.response?.status === 404) {
        errorMessage = 'Authentication service not available. Please ensure the backend is running.';
      } else if (error.response?.status === 401) {
        errorMessage = 'Invalid email or password. Please try again.';
      } else if (error.response?.status === 422) {
        errorMessage = 'Invalid login data. Please check your email format.';
      } else if (error.code === 'ECONNREFUSED' || error.name === 'NetworkError') {
        errorMessage = 'Cannot connect to authentication service. Please check if the backend is running.';
      }
      
      dispatch({
        type: 'LOGIN_ERROR',
        payload: errorMessage,
      });
      throw new Error(errorMessage);
    }
  };

  const loginWithOAuth = async (provider: string) => {
    if (typeof window === 'undefined') return;
    
    try {
      // Generate state for CSRF protection
      const state = Math.random().toString(36).substring(2, 15);
      sessionStorage.setItem('oauth_state', state);
      sessionStorage.setItem('oauth_provider', provider);
      
      // Get OAuth URL and redirect
      const authUrl = authService.getOAuthUrl(provider, state);
      window.location.href = authUrl;
    } catch (error: any) {
      dispatch({
        type: 'LOGIN_ERROR',
        payload: error.message || 'OAuth login failed',
      });
      throw error;
    }
  };

  const logout = async () => {
    try {
      await authService.logout();
    } catch (error) {
      console.warn('Logout API call failed:', error);
    } finally {
      AuthStorage.clear();
      dispatch({ type: 'LOGOUT' });
    }
  };

  const register = async (data: {
    email: string;
    username: string;
    password: string;
    firstName?: string;
    lastName?: string;
  }) => {
    dispatch({ type: 'LOGIN_START' });
    
    try {
      await authService.register(data);
      // After successful registration, login automatically
      await login({ email: data.email, password: data.password });
    } catch (error: any) {
      dispatch({
        type: 'LOGIN_ERROR',
        payload: error.message || 'Registration failed',
      });
      throw error;
    }
  };

  const refreshToken = async () => {
    const currentRefreshToken = AuthStorage.getRefreshToken();
    if (!currentRefreshToken) {
      throw new Error('No refresh token available');
    }

    try {
      const response = await authService.refreshToken(currentRefreshToken);
      
      AuthStorage.setToken(response.data.token);
      AuthStorage.setRefreshToken(response.data.refreshToken);
      AuthStorage.setUser(response.data.user);

      dispatch({
        type: 'LOGIN_SUCCESS',
        payload: {
          user: response.data.user,
          token: response.data.token,
          refreshToken: response.data.refreshToken,
        },
      });

      dispatch({ type: 'TOKEN_REFRESH' });
    } catch (error: any) {
      AuthStorage.clear();
      dispatch({ type: 'LOGOUT' });
      throw error;
    }
  };

  const checkAuth = async () => {
    if (!state.token) return;

    try {
      const user = await authService.getCurrentUser();
      if (user) {
        AuthStorage.setUser(user);
        dispatch({
          type: 'LOGIN_SUCCESS',
          payload: {
            user,
            token: state.token,
            refreshToken: state.refreshToken || '',
          },
        });
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      // Try to refresh token if available
      if (state.refreshToken) {
        try {
          await refreshToken();
        } catch (refreshError) {
          await logout();
        }
      } else {
        await logout();
      }
    }
  };

  const contextValue: AuthContextType = {
    state,
    login,
    loginWithOAuth,
    logout,
    register,
    refreshToken,
    checkAuth,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
}

// Hook to use auth context
export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

// Hook to get current user
export function useUser() {
  const { state } = useAuth();
  return state.user;
}

// Hook to check if user is authenticated
export function useIsAuthenticated() {
  const { state } = useAuth();
  return state.isAuthenticated;
}
