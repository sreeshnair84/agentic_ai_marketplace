import './globals.css';
import Navigation from '@/components/navigation/Navigation';
import { ProjectProvider } from '@/store/projectContext';
import { AuthProvider } from '@/store/authContext';

export const metadata = {
  title: 'Agentic AI Acceleration',
  description: 'Low-code/No-code platform for multi-agent system management',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <AuthProvider>
          <ProjectProvider>
            <Navigation>
              {children}
            </Navigation>
          </ProjectProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
