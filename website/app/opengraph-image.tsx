import { ImageResponse } from 'next/og';

// Image metadata
export const alt = 'Smart AI Memory - Building the Future of AI-Human Collaboration';
export const size = {
  width: 1200,
  height: 630,
};

export const contentType = 'image/png';

// Image generation
export default async function Image() {
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
        <div style={{ fontSize: 80, fontWeight: 'bold', marginBottom: 20 }}>
          Smart AI Memory
        </div>
        <div style={{ fontSize: 36, textAlign: 'center', opacity: 0.9 }}>
          Building the Future of AI-Human Collaboration
        </div>
      </div>
    ),
    {
      ...size,
    }
  );
}
