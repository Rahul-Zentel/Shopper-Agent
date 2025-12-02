import type { NextRequest } from 'next/server'
import { NextResponse } from 'next/server'

import { auth0 } from './lib/auth0'

export async function middleware(request: NextRequest) {
  try {
    return await auth0.middleware(request)
  } catch (error) {
    // Handle JWE decryption errors (usually from stale/invalid cookies)
    if (error instanceof Error && error.message.includes('decryption operation failed')) {
      console.error('Auth0 JWE decryption failed - clearing cookies and continuing request')

      // Clear cookies and let the request continue
      // This will allow Auth0 to handle the unauthenticated state naturally
      const response = NextResponse.next()

      // Clear all Auth0-related cookies
      const cookiesToClear = [
        'appSession',
        'appSession.0',
        'appSession.1',
        'auth_verification'
      ]

      cookiesToClear.forEach(cookieName => {
        response.cookies.delete(cookieName)
      })

      return response
    }

    // Re-throw other errors
    throw error
  }
}

export const config = {
  matcher: [
    // Exclude Auth0 API routes, Next.js internals, and static files
    '/((?!api/auth|_next/static|_next/image|favicon.ico|sitemap.xml|robots.txt).*)'
  ]
}
