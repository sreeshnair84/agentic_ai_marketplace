import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  // Temporarily disable standalone output due to Windows symlink permissions
  // output: 'standalone',
  // Enable static optimization
  trailingSlash: false,
  // Disable ESLint during builds to focus on functionality
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    // Allow builds to continue even with TypeScript errors
    ignoreBuildErrors: false,
  },
  // Enable verbose logging for debugging
  logging: {
    fetches: {
      fullUrl: true,
    },
  },
  // API configuration
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.INTERNAL_GATEWAY_URL || process.env.NEXT_PUBLIC_GATEWAY_URL || 'http://localhost:8000'}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
