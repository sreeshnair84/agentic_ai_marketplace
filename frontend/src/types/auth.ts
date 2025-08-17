// Authentication-related type definitions
export interface LoginRequest {
  email: string;
  password: string;
  rememberMe?: boolean;
}

export interface LoginResponse {
  success: boolean;
  data: {
    token: string;
    refreshToken: string;
    expiresAt: string;
    user: AuthUser;
  };
}

export interface AuthUser {
  id: string;
  email: string;
  username: string;
  firstName?: string;
  lastName?: string;
  role: 'admin' | 'user' | 'viewer';
  isActive: boolean;
  lastLoginAt?: string;
  createdAt: string;
  updatedAt: string;
}

export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
  firstName?: string;
  lastName?: string;
}

export interface RefreshTokenRequest {
  refreshToken: string;
}

export interface AuthState {
  user: AuthUser | null;
  token: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

// OAuth Provider Types
export interface OAuthProvider {
  name: string;
  id: string;
  authUrl: string;
  tokenUrl: string;
  userInfoUrl: string;
  clientId: string;
  scopes: string[];
  enabled: boolean;
}

export interface OAuthConfig {
  providers: Record<string, OAuthProvider>;
  defaultProvider?: string;
  enableLocalAuth: boolean;
}

export interface OAuthLoginRequest {
  provider: string;
  code: string;
  state?: string;
  redirectUri: string;
}

// Authentication Provider Interface
export interface AuthProvider {
  name: string;
  login(credentials: LoginRequest | OAuthLoginRequest): Promise<LoginResponse>;
  logout(): Promise<void>;
  refreshToken(refreshToken: string): Promise<LoginResponse>;
  getCurrentUser(): Promise<AuthUser>;
  isConfigured(): boolean;
}

// Auth Events
export type AuthEvent = 
  | { type: 'LOGIN_START' }
  | { type: 'LOGIN_SUCCESS'; payload: { user: AuthUser; token: string; refreshToken: string } }
  | { type: 'LOGIN_ERROR'; payload: string }
  | { type: 'LOGOUT' }
  | { type: 'TOKEN_REFRESH' }
  | { type: 'AUTH_ERROR'; payload: string };

export interface AuthContextType {
  state: AuthState;
  login: (credentials: LoginRequest) => Promise<void>;
  loginWithOAuth: (provider: string) => Promise<void>;
  logout: () => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  refreshToken: () => Promise<void>;
  checkAuth: () => Promise<void>;
}
