'use client';

import Navigation from '@/components/navigation/Navigation';
import { ProjectProvider } from '@/store/projectContext';
import { AuthProvider } from '@/store/authContext';

interface ClientWrapperProps {
  children: React.ReactNode;
}

export default function ClientWrapper({ children }: ClientWrapperProps) {
  return (
    <AuthProvider>
      <ProjectProvider>
        <Navigation>
          {children}
        </Navigation>
      </ProjectProvider>
    </AuthProvider>
  );
}