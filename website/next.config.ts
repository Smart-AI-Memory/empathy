import type { NextConfig } from "next";
import path from "path";

const nextConfig: NextConfig = {
  output: 'standalone',
  outputFileTracingRoot: path.join(__dirname, './'),
  eslint: {
    // Only run ESLint on these directories during production builds
    dirs: ['app'],
    // Ignore ESLint errors during production builds
    ignoreDuringBuilds: true,
  },
  async rewrites() {
    return [
      // Serve index.html for framework-docs directory requests
      {
        source: '/framework-docs/:path*/',
        destination: '/framework-docs/:path*/index.html',
      },
      {
        source: '/framework-docs/:path((?!.*\\.).*)',
        destination: '/framework-docs/:path/index.html',
      },
    ];
  },
};

export default nextConfig;
