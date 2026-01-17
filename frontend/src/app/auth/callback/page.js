'use client';

import { useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';

function CallbackContent() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const { handleCallback } = useAuth();

    useEffect(() => {
        const processCallback = async () => {
            // Check for code in URL params (from OAuth redirect)
            const code = searchParams.get('code');

            // Check for token in URL hash (direct token)
            const hash = window.location.hash;
            const hashParams = new URLSearchParams(hash.substring(1));
            const accessToken = hashParams.get('access_token');

            if (accessToken) {
                // Token provided directly in hash
                localStorage.setItem('access_token', accessToken);
                router.push('/dashboard');
            } else if (code) {
                // Exchange code for token
                try {
                    await handleCallback(code);
                    router.push('/dashboard');
                } catch (error) {
                    console.error('Callback error:', error);
                    router.push('/login?error=auth_failed');
                }
            } else {
                // No code or token, redirect to login
                router.push('/login');
            }
        };

        processCallback();
    }, [searchParams, handleCallback, router]);

    return (
        <div className="auth-page">
            <div className="auth-container">
                <div className="auth-card" style={{ textAlign: 'center' }}>
                    <div className="auth-logo">NEXARCH</div>
                    <h1 className="auth-title display-title display-md">
                        AUTHENTICATING
                    </h1>
                    <div className="auth-loading-spinner">
                        <div className="spinner"></div>
                    </div>
                    <p className="auth-subtitle">
                        Please wait while we complete your sign in...
                    </p>
                </div>
            </div>
        </div>
    );
}

export default function AuthCallback() {
    return (
        <Suspense fallback={
            <div className="auth-page">
                <div className="auth-container">
                    <div className="auth-card" style={{ textAlign: 'center' }}>
                        <div className="auth-loading">Loading...</div>
                    </div>
                </div>
            </div>
        }>
            <CallbackContent />
        </Suspense>
    );
}
