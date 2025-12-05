import type { NextRequest } from 'next/server'
import { NextResponse } from 'next/server'

// Simple no-op middleware to satisfy Next.js; does not use Auth0 or perform auth.
export function middleware(_request: NextRequest) {
  return NextResponse.next()
}

// Apply to all paths (you can remove this export entirely if you don't need any middleware).
export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico|sitemap.xml|robots.txt).*)'],
}


