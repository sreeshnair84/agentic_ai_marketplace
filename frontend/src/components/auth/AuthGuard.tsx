'use client';

import React from 'react';
import { useAuth } from '@/store/authContext';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

interface AuthGuardProps {
  children: React.ReactNode;
  requireAuth?: boolean;
  redirectTo?: string;
}

/**
 * Authentication guard component that protects routes
 */
export function AuthGuard({ 
  children, 
  requireAuth = true, 
  redirectTo = '/auth/login' 
}: AuthGuardProps) {
  const { state } = useAuth();
  const router = useRouter();

  useEffect(() => {
    console.log('AuthGuard: Auth state check', {
      isAuthenticated: state.isAuthenticated,
      isLoading: state.isLoading,
      error: state.error,
      requireAuth
    });

    if (requireAuth && !state.isLoading && !state.isAuthenticated) {
      console.log('AuthGuard: Redirecting to login because user is not authenticated');
      router.push(redirectTo);
    }
  }, [state.isAuthenticated, state.isLoading, requireAuth, redirectTo, router]);

  // Show loading while checking auth
  if (state.isLoading) {
    console.log('AuthGuard: Showing loading state');
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Checking authentication...</p>
        </div>
      </div>
    );
  }

  // Show auth error if present
  if (state.error && requireAuth) {
    console.log('AuthGuard: Auth error present', state.error);
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center max-w-md mx-auto p-6">
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
            <h3 className="text-red-800 font-semibold mb-2">Authentication Error</h3>
            <p className="text-red-600 text-sm">{state.error}</p>
          </div>
          <button
            onClick={() => router.push('/auth/login')}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            Go to Login
          </button>
        </div>
      </div>
    );
  }

  // Don't render children if auth is required but user is not authenticated
  if (requireAuth && !state.isAuthenticated) {
    console.log('AuthGuard: Not rendering children, user not authenticated');
    return null;
  }

  console.log('AuthGuard: Rendering children, user is authenticated');
  return <>{children}</>;
}

interface PublicRouteProps {
  children: React.ReactNode;
  redirectTo?: string;
}

/**
 * Component for public routes that redirect authenticated users
 */
export function PublicRoute({ children, redirectTo = '/dashboard' }: PublicRouteProps) {
  const { state } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!state.isLoading && state.isAuthenticated) {
      router.push(redirectTo);
    }
  }, [state.isAuthenticated, state.isLoading, redirectTo, router]);

  // Show loading while checking auth
  if (state.isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading...</p>
        </div>
      </div>
    );
  }

  // Don't render children if user is authenticated (they should be redirected)
  if (state.isAuthenticated) {
    return null;
  }

  return <>{children}</>;
}
