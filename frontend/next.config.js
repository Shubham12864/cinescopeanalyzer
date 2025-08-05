/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  output: 'standalone', // Enable standalone output for Docker
  
  // Fix chunk loading errors
  webpack: (config, { isServer }) => {
    if (!isServer) {
      config.optimization.splitChunks = {
        chunks: 'all',
        cacheGroups: {
          default: {
            name: 'commons',
            minChunks: 2,
            chunks: 'all',
            enforce: true,
          },
        },
      };
    }
    return config;
  },
  
  // Enable experimental features for stability
  experimental: {
    optimizePackageImports: ['@tanstack/react-query'],
  },
  
  images: {
    domains: [
      'localhost',
      '127.0.0.1',
      'assets.fanart.tv',        // Add FanArt domains for image loading
      'fanart.tv',
      'image.tmdb.org',
      'm.media-amazon.com',
      'media-amazon.com',
      'images-amazon.com',
      'ia.media-imdb.com',
      'imdb.com',
      'www.imdb.com',
      'via.placeholder.com',
      'dummyimage.com',
      'res.cloudinary.com',
      'cloudinary.com',
      'cinescopeanalyzer-production.up.railway.app'
    ],
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'assets.fanart.tv',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'fanart.tv',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'image.tmdb.org',
        port: '',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'm.media-amazon.com',
        port: '',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'media-amazon.com',
        port: '',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'images-amazon.com',
        port: '',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'ia.media-imdb.com',
        port: '',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'via.placeholder.com',
        port: '',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'dummyimage.com',
        port: '',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'res.cloudinary.com',
        port: '',
        pathname: '/**',
      },
      {
        protocol: 'http',
        hostname: 'localhost',
        port: '8000',
        pathname: '/api/movies/images/cached/**',
      }
    ],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
    minimumCacheTTL: 60,
    unoptimized: true
  },
  typescript: {
    ignoreBuildErrors: false
  },
  eslint: {
    ignoreDuringBuilds: false
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/:path*`,
      },
    ];
  },
}

module.exports = nextConfig
