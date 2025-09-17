import React, { createContext, useState, useContext, useEffect } from 'react';

const AuthContext = createContext();

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};

export const AuthProvider = ({ children }) => {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    // Check for existing token on app startup
    useEffect(() => {
        const token = localStorage.getItem('accessToken');
        const userData = localStorage.getItem('userData');
        
        if (token && userData) {
            try {
                const parsedUser = JSON.parse(userData);
                setUser(parsedUser);
                setIsAuthenticated(true);
            } catch (error) {
                console.error('Error parsing user data:', error);
                logout();
            }
        }
        setLoading(false);
    }, []);

    const login = async (credentials) => {
        try {
            const response = await fetch('http://localhost:8000/api/auth/login/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(credentials),
            });

            const data = await response.json();

            if (response.ok && data.access) {
                // Store tokens and user data
                localStorage.setItem('accessToken', data.access);
                localStorage.setItem('refreshToken', data.refresh);
                localStorage.setItem('userData', JSON.stringify(data.user));

                setUser(data.user);
                setIsAuthenticated(true);
                return { success: true };
            } else {
                return { 
                    success: false, 
                    message: data.message || 'Login failed. Please check your credentials.' 
                };
            }
        } catch (error) {
            console.error('Login error:', error);
            return { 
                success: false, 
                message: 'Network error. Please check your connection and try again.' 
            };
        }
    };

    const logout = () => {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('userData');
        setUser(null);
        setIsAuthenticated(false);
    };

    const getToken = () => {
        return localStorage.getItem('accessToken');
    };

    const value = {
        isAuthenticated,
        user,
        loading,
        login,
        logout,
        getToken,
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
};