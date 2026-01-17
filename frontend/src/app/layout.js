import { Inter } from 'next/font/google';
import './globals.css';
import { AuthProvider } from '@/lib/auth-context';

const inter = Inter({
    subsets: ['latin'],
    variable: '--font-inter',
    display: 'swap',
});

export const metadata = {
    title: 'NEXRCH | System Design Made Visual',
    description: 'Design, visualize, and iterate on complex system architectures with ease. The ultimate platform for engineers who think in systems.',
    keywords: ['system design', 'architecture', 'diagrams', 'microservices', 'distributed systems', 'engineering'],
    openGraph: {
        title: 'NEXRCH | System Design Made Visual',
        description: 'Design, visualize, and iterate on complex system architectures with ease.',
        type: 'website',
    },
};

export default function RootLayout({ children }) {
    return (
        <html lang="en">
            <head>
                <link rel="preconnect" href="https://fonts.googleapis.com" />
                <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
                <link
                    href="https://fonts.googleapis.com/css2?family=Bebas+Neue&display=swap"
                    rel="stylesheet"
                />
            </head>
            <body className={inter.variable}>
                <AuthProvider>
                    {children}
                </AuthProvider>
            </body>
        </html>
    );
}
