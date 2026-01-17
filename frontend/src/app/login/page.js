'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/lib/auth-context';
import { Chrome } from 'lucide-react';

export default function LoginPage() {
    const router = useRouter();
    const { loginWithGoogle, isAuthenticated, loading } = useAuth();
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!loading && isAuthenticated) {
            router.push('/dashboard');
        }
    }, [isAuthenticated, loading, router]);

    const handleGoogleLogin = async () => {
        setIsLoading(true);
        setError(null);
        try {
            await loginWithGoogle();
        } catch (err) {
            setError('Failed to connect to authentication service. Please try again.');
            setIsLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="auth-page">
                <div className="auth-container">
                    <div className="auth-loading">Loading...</div>
                </div>
            </div>
        );
    }

    return (
        <div className="auth-page">
            {/* Halftone decorations */}
            <div className="halftone-corner halftone-corner--top-right" />
            <div className="halftone-corner halftone-corner--bottom-left" />

            <div className="auth-container">
                <div className="auth-card">
                    {/* Header */}
                    <div className="auth-header">
                        <Link href="/" className="auth-logo">NEXRCH</Link>
                        <span className="tape-label tape-label--rotated">WELCOME BACK</span>
                    </div>

                    {/* Title */}
                    <h1 className="auth-title display-title display-md">
                        SIGN IN
                    </h1>

                    <p className="auth-subtitle">
                        Access your system architecture dashboard and AI-powered design tools.
                    </p>

                    {/* Error Message */}
                    {error && (
                        <div className="auth-error">
                            {error}
                        </div>
                    )}

                    {/* Google Sign In Button */}
                    <button
                        onClick={handleGoogleLogin}
                        disabled={isLoading}
                        className="btn-google"
                    >
                        <Chrome size={20} />
                        <span>{isLoading ? 'Connecting...' : 'Continue with Google'}</span>
                    </button>

                    {/* Divider */}
                    <div className="auth-divider">
                        <span>SECURE AUTHENTICATION</span>
                    </div>

                    {/* Info */}
                    <div className="auth-info">
                        <p>By signing in, you agree to our Terms of Service and Privacy Policy.</p>
                    </div>

                    {/* Footer */}
                    <div className="auth-footer">
                        <p>Don't have an account?</p>
                        <Link href="/signup" className="auth-link">
                            Create Account
                        </Link>
                    </div>
                </div>

                {/* Side decoration */}
                <div className="auth-decoration">
                    <div className="auth-decoration__grid">
                        {[...Array(16)].map((_, i) => (
                            <div key={i} className="auth-decoration__cell" />
                        ))}
                    </div>
                    <div className="auth-decoration__text">
                        <span className="display-title">SYSTEM</span>
                        <span className="display-title">DESIGN</span>
                        <span className="display-title">MADE</span>
                        <span className="display-title">VISUAL</span>
                    </div>
                </div>
            </div>
        </div>
    );
}
