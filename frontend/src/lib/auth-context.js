'use client';

import { createContext, useContext, useState, useEffect } from 'react';
import { apiClient } from '@/lib/api-client';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [isAuthenticated, setIsAuthenticated] = useState(false);

    // Check authentication status on mount
    useEffect(() => {
        checkAuth();
    }, []);

    const checkAuth = async () => {
        try {
            const token = apiClient.getToken();
            if (token) {
                const userData = await apiClient.getCurrentUser();
                setUser(userData);
                setIsAuthenticated(true);
            }
        } catch (error) {
            console.error('Auth check failed:', error);
            apiClient.removeToken();
            setUser(null);
            setIsAuthenticated(false);
        } finally {
            setLoading(false);
        }
    };

    const loginWithGoogle = async () => {
        try {
            const { auth_url } = await apiClient.getGoogleAuthUrl();
            window.location.href = auth_url;
        } catch (error) {
            console.error('Failed to get Google auth URL:', error);
            throw error;
        }
    };

    const handleCallback = async (code) => {
        try {
            const result = await apiClient.googleSignIn(code);
            setUser(result.user);
            setIsAuthenticated(true);
            return result;
        } catch (error) {
            console.error('Google sign in failed:', error);
            throw error;
        }
    };

    const logout = async () => {
        try {
            await apiClient.logout();
        } finally {
            setUser(null);
            setIsAuthenticated(false);
        }
    };

    return (
        <AuthContext.Provider
            value={{
                user,
                loading,
                isAuthenticated,
                loginWithGoogle,
                handleCallback,
                logout,
                checkAuth,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}
