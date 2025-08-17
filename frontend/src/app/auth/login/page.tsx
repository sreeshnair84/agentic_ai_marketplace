'use client';

import { LoginForm } from '@/components/auth/LoginForm';
import { PublicRoute } from '@/components/auth/AuthGuard';
import { useRouter } from 'next/navigation';

export default function LoginPage() {
  const router = useRouter();

  const handleSuccess = () => {
    router.push('/dashboard');
  };

  return (
    <PublicRoute>
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
        <LoginForm onSuccess={handleSuccess} />
      </div>
    </PublicRoute>
  );
}
