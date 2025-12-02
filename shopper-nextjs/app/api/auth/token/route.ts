import { NextResponse } from 'next/server'
import { auth0 } from '@/lib/auth0'

export async function GET() {
  try {
    const session = await auth0.getSession()

    if (!session) {
      return NextResponse.json({ accessToken: null }, { status: 401 })
    }

    return NextResponse.json({ accessToken: session.accessToken })
  } catch (error) {
    console.error('Error getting access token:', error)
    return NextResponse.json({ accessToken: null }, { status: 500 })
  }
}
