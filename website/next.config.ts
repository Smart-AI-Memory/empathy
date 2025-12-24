import type { NextConfig } from "next";
import path from "path";

const nextConfig: NextConfig = {
  output: 'standalone',
  outputFileTracingRoot: path.join(__dirname, './'),
  trailingSlash: true,  // Force trailing slashes for MkDocs compatibility
  eslint: {
    // Only run ESLint on these directories during production builds
    dirs: ['app'],
    // Ignore ESLint errors during production builds
    ignoreDuringBuilds: true,
  },
};

export default nextConfig;
