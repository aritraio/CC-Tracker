import type { Metadata } from 'next';
import { Outfit, JetBrains_Mono } from 'next/font/google';
import './globals.css';
import { BauhausLogo } from '@/components/ui/BauhausLogo';
import Link from 'next/link';

const outfit = Outfit({
  subsets: ['latin'],
  weight: ['400', '500', '700', '900'],
  variable: '--font-outfit',
  display: 'swap',
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  weight: ['500', '700'],
  variable: '--font-mono',
  display: 'swap',
});

export const metadata: Metadata = {
  title: 'CC Track — Personal Spending Intelligence & Behavioral Financial Coach',
  description:
    'Turn unstructured credit card statements into mathematically validated transactions and deterministic spending intelligence with zero-knowledge client decryption.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${outfit.variable} ${jetbrainsMono.variable}`}>
      <body className="min-h-screen bg-canvas text-ink font-sans flex flex-col selection:bg-bauhaus-yellow selection:text-ink antialiased">
        {/* Navigation Bar */}
        <header className="sticky top-0 z-50 bg-paper border-b-2 md:border-b-4 border-black">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 md:h-20 flex items-center justify-between">
            <BauhausLogo size="md" />

            <nav className="hidden md:flex items-center gap-8">
              <Link
                href="/"
                className="text-xs font-bold uppercase tracking-widest text-ink hover:text-bauhaus-red transition-colors"
              >
                Upload
              </Link>
              <Link
                href="#features"
                className="text-xs font-bold uppercase tracking-widest text-ink hover:text-bauhaus-blue transition-colors"
              >
                Architecture
              </Link>
              <Link
                href="#security"
                className="text-xs font-bold uppercase tracking-widest text-ink hover:text-bauhaus-green transition-colors"
              >
                Privacy
              </Link>
              <a
                href="http://localhost:8000/api/v1/docs"
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs font-bold uppercase tracking-widest text-ink hover:text-bauhaus-yellow transition-colors"
              >
                API Docs
              </a>
            </nav>

            <div className="flex items-center gap-3">
              <div className="hidden sm:flex items-center gap-2 px-3 py-1 bg-muted border-2 border-black font-mono text-xs font-bold">
                <span className="w-2 h-2 rounded-full bg-bauhaus-green inline-block animate-pulse" />
                <span>API ONLINE</span>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="flex-1">{children}</main>

        {/* Constructivist Footer */}
        <footer className="bg-ink text-white border-t-4 border-black py-12 px-4 sm:px-6 lg:px-8">
          <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex items-center gap-3">
              <div className="w-4 h-4 rounded-full bg-bauhaus-red border border-white" />
              <div className="w-4 h-4 bg-bauhaus-blue border border-white" />
              <div className="w-4 h-4 bg-bauhaus-yellow bauhaus-clip-triangle" />
              <span className="font-black tracking-tighter text-lg uppercase">
                CC TRACK
              </span>
            </div>
            <div className="text-xs text-white/70 text-center font-mono">
              MATHEMATICAL TRUTH • CLIENT-SIDE ZERO-KNOWLEDGE • ZERO HALLUCINATIONS
            </div>
            <div className="text-xs font-bold uppercase tracking-widest text-bauhaus-yellow">
              © {new Date().getFullYear()} CC Track Platform
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
