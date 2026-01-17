'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/lib/auth-context';
import { Chrome, Zap, Shield, Cpu } from 'lucide-react';

export default function SignupPage() {
    const router = useRouter();
    const { loginWithGoogle, isAuthenticated, loading } = useAuth();
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!loading && isAuthenticated) {
            router.push('/dashboard');
        }
    }, [isAuthenticated, loading, router]);

    const handleGoogleSignup = async () => {
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
                        <span className="tape-label">JOIN NOW</span>
                    </div>

                    {/* Title */}
                    <h1 className="auth-title display-title display-md">
                        CREATE ACCOUNT
                    </h1>

                    <p className="auth-subtitle">
                        Start designing system architectures with AI-powered tools. Free forever.
                    </p>

                    {/* Features */}
                    <div className="auth-features">
                        <div className="auth-feature">
                            <Cpu size={18} />
                            <span>Visual Architecture Design</span>
                        </div>
                        <div className="auth-feature">
                            <Zap size={18} />
                            <span>AI-Powered Recommendations</span>
                        </div>
                        <div className="auth-feature">
                            <Shield size={18} />
                            <span>Enterprise-Grade Security</span>
                        </div>
                    </div>

                    {/* Error Message */}
                    {error && (
                        <div className="auth-error">
                            {error}
                        </div>
                    )}

                    {/* Google Sign Up Button */}
                    <button
                        onClick={handleGoogleSignup}
                        disabled={isLoading}
                        className="btn-google"
                    >
                        <Chrome size={20} />
                        <span>{isLoading ? 'Connecting...' : 'Sign up with Google'}</span>
                    </button>

                    {/* Divider */}
                    <div className="auth-divider">
                        <span>NO CREDIT CARD REQUIRED</span>
                    </div>

                    {/* Info */}
                    <div className="auth-info">
                        <p>By creating an account, you agree to our Terms of Service and Privacy Policy.</p>
                    </div>

                    {/* Footer */}
                    <div className="auth-footer">
                        <p>Already have an account?</p>
                        <Link href="/login" className="auth-link">
                            Sign In
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
                        <span className="display-title">DESIGN</span>
                        <span className="display-title">BUILD</span>
                        <span className="display-title">SCALE</span>
                        <span className="display-title">DEPLOY</span>
                    </div>
                </div>
            </div>
        </div>
    );
}
