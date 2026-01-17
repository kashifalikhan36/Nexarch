'use client';

import Link from 'next/link';
import { useAuth } from '@/lib/auth-context';
import { User, LogOut } from 'lucide-react';

export default function Navbar() {
    const { user, isAuthenticated, logout, loading } = useAuth();

    const handleLogout = async () => {
        await logout();
        window.location.href = '/';
    };

    return (
        <nav className="navbar">
            <Link href="/" className="navbar__logo">NEXRCH</Link>

            <div className="navbar__links">
                <Link href="/#features" className="navbar__link">Features</Link>
                <Link href="/dashboard" className="navbar__link">Dashboard</Link>
                <Link href="/ai-design" className="navbar__link">AI Design</Link>
                <Link href="/architecture" className="navbar__link">Architecture</Link>

                {loading ? (
                    <span className="navbar__loading">...</span>
                ) : isAuthenticated ? (
                    <div className="navbar__user">
                        <span className="navbar__user-name">
                            <User size={16} />
                            {user?.name || user?.email || 'User'}
                        </span>
                        <button onClick={handleLogout} className="btn btn-secondary navbar__logout">
                            <LogOut size={14} />
                            Logout
                        </button>
                    </div>
                ) : (
                    <>
                        <Link href="/login" className="navbar__link">Login</Link>
                        <Link href="/signup" className="btn btn-primary navbar__cta">
                            Get Started
                        </Link>
                    </>
                )}
            </div>
        </nav>
    );
}
