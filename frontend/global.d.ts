// Global type declarations for the CineScopeAnalyzer frontend

declare module '*.svg' {
  const content: React.FunctionComponent<React.SVGAttributes<SVGElement>>
  export default content
}

declare module '*.png' {
  const content: string
  export default content
}

declare module '*.jpg' {
  const content: string
  export default content
}

declare module '*.jpeg' {
  const content: string
  export default content
}

declare module '*.gif' {
  const content: string
  export default content
}

declare module '*.webp' {
  const content: string
  export default content
}

// Extend Window interface for any global properties
interface Window {
  gtag?: (...args: any[]) => void
}

// Environment variables
declare namespace NodeJS {
  interface ProcessEnv {
    NEXT_PUBLIC_API_URL: string
    NEXT_PUBLIC_OMDB_API_KEY: string
    NEXT_PUBLIC_APP_NAME: string
    NEXT_PUBLIC_APP_VERSION: string
    NEXT_PUBLIC_IMAGE_PROXY_ENABLED: string
    NODE_ENV: 'development' | 'production' | 'test'
  }
}
