import { NextRequest, NextResponse } from 'next/server';

// Gate the admin dashboard (root) behind the admin_token cookie.
// Everything else — /sites/*, /preview/*, /login, static assets — stays public.
export function middleware(req: NextRequest) {
  const token = req.cookies.get('admin_token')?.value;
  if (!token) {
    const url = req.nextUrl.clone();
    url.pathname = '/login';
    return NextResponse.redirect(url);
  }
  return NextResponse.next();
}

export const config = {
  // Only run on the dashboard root. Public site routes are never matched.
  matcher: ['/'],
};
