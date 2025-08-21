import './globals.css';
import { Inter } from 'next/font/google';
import Navigation from '@/components/navigation/Navigation';
import { ProjectProvider } from '@/store/projectContext';
import { AuthProvider } from '@/store/authContext';

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
});

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
    <html lang="en" className={inter.variable}>
      <body className={`${inter.className} min-h-screen bg-gray-50 dark:bg-gray-900 font-sans antialiased`}>
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
