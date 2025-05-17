
/** @type {import('next').NextConfig} */
const nextConfig = {
  // Explicitly set React strictMode
  reactStrictMode: true,
  
  // Add output configuration for standalone build
  output: 'standalone',
  
  // Enable static exports if needed
  // output: 'export',
  
  // Disable server-side rendering for API-dependent pages
  experimental: {
    // Allow opting out of server components  
    appDir: true,
  },
  
  // Configure environment variables that should be available at build time
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
  
  // Configure image domains for next/image optimization if needed
  images: {
    domains: ['localhost'],
  },
  
  // Configure webpack if needed
  webpack(config) {
    return config;
  },
}

module.exports = nextConfig