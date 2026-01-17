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
        setLoading(true);
        try {
            const token = apiClient.getToken();
            if (token) {
                try {
                    const userData = await apiClient.getCurrentUser();
                    setUser(userData);
                    setIsAuthenticated(true);
                } catch (apiError) {
                    // Only remove token if we get 401 (unauthorized)
                    // Don't remove on network errors or other issues
                    if (apiError.message === 'Unauthorized') {
                        console.error('Token invalid, clearing auth');
                        apiClient.removeToken();
                        setUser(null);
                        setIsAuthenticated(false);
                    } else {
                        // Network error or other issue - keep token, just log it
                        console.warn('Auth check had non-fatal error:', apiError.message);
                        // Keep isAuthenticated if we have a token
                        setIsAuthenticated(true);
                    }
                }
            } else {
                // No token, not authenticated
                setUser(null);
                setIsAuthenticated(false);
            }
        } catch (error) {
            console.error('Auth check failed:', error);
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

    const loginWithEmail = async (email, password) => {
        try {
            await apiClient.login(email, password);
            // Set authenticated immediately
            setIsAuthenticated(true);
            // Then fetch user data in background
            try {
                const userData = await apiClient.getCurrentUser();
                setUser(userData);
            } catch (userError) {
                console.error('Failed to fetch user data:', userError);
                // Continue anyway since we have the token
            }
        } catch (error) {
            console.error('Email login failed:', error);
            setIsAuthenticated(false);
            throw error;
        }
    };

    const signupWithEmail = async (email, password, fullName) => {
        try {
            await apiClient.signup(email, password, fullName);
            // Set authenticated immediately
            setIsAuthenticated(true);
            // Then fetch user data in background
            try {
                const userData = await apiClient.getCurrentUser();
                setUser(userData);
            } catch (userError) {
                console.error('Failed to fetch user data:', userError);
                // Continue anyway since we have the token
            }
        } catch (error) {
            console.error('Email signup failed:', error);
            setIsAuthenticated(false);
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
                loginWithEmail,
                signupWithEmail,
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
