import type React from "react"
import type { Metadata } from "next"
import { Inter, Poppins } from "next/font/google"
import "./globals.css"
import { Providers } from "./providers"
import ChunkErrorBoundary from "@/components/error-boundary/chunk-error-boundary"
import ServiceWorkerRegistration from "@/components/ServiceWorkerRegistration"

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
})

const poppins = Poppins({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-poppins",
  display: "swap",
})

export const metadata: Metadata = {
  title: "CineAnalyzer - Movie Review Intelligence",
  description: "Advanced movie review analysis with AI-powered insights",
  keywords: "movie reviews, sentiment analysis, cinema, film analysis",
    generator: 'v0.dev'
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.variable} ${poppins.variable} font-sans antialiased`}>
        <ChunkErrorBoundary>
          <Providers>
            <ServiceWorkerRegistration />
            <div className="min-h-screen bg-gradient-to-b from-black via-gray-900 to-black">
              <div className="absolute inset-0 bg-[url('/grid.svg')] bg-center [mask-image:linear-gradient(180deg,white,rgba(255,255,255,0))]" />
              <div className="relative">{children}</div>
            </div>
          </Providers>
        </ChunkErrorBoundary>
      </body>
    </html>
  )
}
