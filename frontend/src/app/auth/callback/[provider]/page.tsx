'use client';

import { useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuth } from '@/store/authContext';
import { authService } from '@/lib/auth/authService';

export default function OAuthCallbackPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { state } = useAuth();

  useEffect(() => {
    const handleOAuthCallback = async () => {
      const code = searchParams.get('code');
      const state = searchParams.get('state');
      const error = searchParams.get('error');
      
      // Get stored OAuth state and provider
      const storedState = sessionStorage.getItem('oauth_state');
      const provider = sessionStorage.getItem('oauth_provider');

      // Clear stored data
      sessionStorage.removeItem('oauth_state');
      sessionStorage.removeItem('oauth_provider');

      if (error) {
        console.error('OAuth error:', error);
        router.push('/auth/login?error=' + encodeURIComponent(error));
        return;
      }

      if (!code || !state || !provider) {
        console.error('Missing OAuth parameters');
        router.push('/auth/login?error=missing_parameters');
        return;
      }

      if (state !== storedState) {
        console.error('OAuth state mismatch');
        router.push('/auth/login?error=state_mismatch');
        return;
      }

      try {
        // Handle OAuth login
        await authService.loginWithOAuth(provider, {
          provider,
          code,
          state,
          redirectUri: window.location.origin + '/auth/callback/' + provider
        });
        
        router.push('/dashboard');
      } catch (error: any) {
        console.error('OAuth login failed:', error);
        router.push('/auth/login?error=' + encodeURIComponent(error.message || 'oauth_failed'));
      }
    };

    handleOAuthCallback();
  }, [searchParams, router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-gray-600 dark:text-gray-400">
          Completing authentication...
        </p>
      </div>
    </div>
  );
}
