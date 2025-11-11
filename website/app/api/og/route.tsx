import { ImageResponse } from 'next/og';
import { NextRequest } from 'next/server';

export const runtime = 'edge';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);

    // Get parameters from query string
    const title = searchParams.get('title') || 'Smart AI Memory';
    const subtitle = searchParams.get('subtitle') || 'Building the Future of AI-Human Collaboration';

    return new ImageResponse(
      (
        <div
          style={{
            fontSize: 60,
            background: 'linear-gradient(135deg, #1E40AF 0%, #06B6D4 50%, #8B5CF6 100%)',
            width: '100%',
            height: '100%',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            fontFamily: 'sans-serif',
            padding: '80px',
          }}
        >
          <div style={{ fontSize: 80, fontWeight: 'bold', marginBottom: 20, textAlign: 'center' }}>
            {title}
          </div>
          <div style={{ fontSize: 36, textAlign: 'center', opacity: 0.9 }}>
            {subtitle}
          </div>
        </div>
      ),
      {
        width: 1200,
        height: 630,
      }
    );
  } catch (e: any) {
    console.log(`${e.message}`);
    return new Response(`Failed to generate the image`, {
      status: 500,
    });
  }
}
