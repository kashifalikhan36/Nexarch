'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/lib/auth-context';
import ApiKeyManager from '@/components/ApiKeyManager';
import { Key } from 'lucide-react';

export default function ApiKeysPage() {
    const { isAuthenticated, loading: authLoading } = useAuth();
    const router = useRouter();

    useEffect(() => {
        if (!authLoading && !isAuthenticated) {
            router.push('/login');
        }
    }, [isAuthenticated, authLoading, router]);

    if (authLoading) {
        return (
            <div className="page-loading">
                <div className="spinner"></div>
                <p>Loading...</p>
            </div>
        );
    }

    if (!isAuthenticated) {
        // Redirect is firing via useEffect; show spinner to prevent flash of content
        return (
            <div className="page-loading">
                <div className="spinner"></div>
                <p>Redirecting...</p>
            </div>
        );
    }

    return (
        <div className="dashboard-page">
            {/* Header */}
            <nav className="dashboard-nav">
                <Link href="/" className="navbar__logo">NEXARCH</Link>
                <div className="dashboard-nav__links">
                    <Link href="/dashboard">Dashboard</Link>
                    <Link href="/ingestion">Ingestion</Link>
                    <Link href="/architecture">Architecture</Link>
                    <Link href="/ai-design">AI Design</Link>
                    <Link href="/api-keys" className="api-link active">
                        <Key size={14} />
                        <span>API Keys</span>
                    </Link>
                </div>
            </nav>

            {/* Page Content */}
            <div className="dashboard-content">
                <div className="dashboard-header">
                    <div>
                        <span className="tape-label">SDK Authentication</span>
                        <h1 className="display-title display-md" style={{ marginTop: '0.5rem' }}>
                            API KEYS
                        </h1>
                        <p className="dashboard-welcome" style={{ marginTop: '0.5rem' }}>
                            Manage authentication keys for the Nexarch SDK
                        </p>
                    </div>
                </div>

                <ApiKeyManager />
            </div>
        </div>
    );
}
