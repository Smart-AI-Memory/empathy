import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const pathname = request.nextUrl.pathname;

  // Handle framework-docs paths - ensure trailing slash for MkDocs relative paths
  if (pathname.startsWith('/framework-docs')) {
    // Skip files with extensions (CSS, JS, images, etc.)
    if (pathname.match(/\.[a-zA-Z0-9]+$/)) {
      return NextResponse.next();
    }

    // Add trailing slash if missing
    if (!pathname.endsWith('/')) {
      const url = request.nextUrl.clone();
      url.pathname = pathname + '/';
      return NextResponse.redirect(url, 308);
    }
  }

  return NextResponse.next();
}

export const config = {
  // Match all framework-docs paths
  matcher: [
    '/framework-docs',
    '/framework-docs/:path*',
  ],
};
