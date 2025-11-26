import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  eslint: {
    // Only run ESLint on these directories during production builds
    dirs: ['app'],
    // Ignore ESLint errors during production builds
    ignoreDuringBuilds: true,
  },
  async redirects() {
    return [
      {
        source: '/framework-docs',
        destination: '/framework-docs/',
        permanent: true,
      },
    ];
  },
};

export default nextConfig;
