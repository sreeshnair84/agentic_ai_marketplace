'use client';

import { AuthGuard } from '@/components/auth/AuthGuard';
import { A2AChatInterface } from '@/components/chat/A2AChatInterface';

export default function ChatPage() {
  return (
    <AuthGuard>
      <A2AChatInterface />
    </AuthGuard>
  );
}
