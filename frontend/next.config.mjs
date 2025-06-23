/** @type {import('next').NextConfig} */
const nextConfig = {
  eslint: {
    ignoreDuringBuilds: false,
  },
  typescript: {
    ignoreBuildErrors: false,
  },
  images: {
    unoptimized: true,
    domains: [
      'image.tmdb.org', 
      'www.imdb.com',
      'm.media-amazon.com',      'media-amazon.com',
      'images-amazon.com',
      'ia.media-imdb.com',
      'via.placeholder.com',
      'res.cloudinary.com',  // Add Cloudinary domain
      'cloudinary.com',      // Add Cloudinary CDN
      'localhost'
    ],
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
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

export default nextConfig