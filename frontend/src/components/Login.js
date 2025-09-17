import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import './Login.css';

const Login = () => {
    const [credentials, setCredentials] = useState({
        username: '',
        password: ''
    });
    const [errors, setErrors] = useState({});
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [showRegister, setShowRegister] = useState(false);
    
    const { login } = useAuth();
    const navigate = useNavigate();

    const validateForm = () => {
        const newErrors = {};
        
        if (!credentials.username.trim()) {
            newErrors.username = 'Username is required';
        }
        
        if (!credentials.password) {
            newErrors.password = 'Password is required';
        } else if (credentials.password.length < 6) {
            newErrors.password = 'Password must be at least 6 characters';
        }
        
        return newErrors;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setErrors({});
        
        // Validate form
        const formErrors = validateForm();
        if (Object.keys(formErrors).length > 0) {
            setErrors(formErrors);
            return;
        }

        setIsSubmitting(true);
        
        try {
            const result = await login(credentials);
            
            if (result.success) {
                navigate('/dashboard');
            } else {
                setErrors({ submit: result.message });
            }
        } catch (error) {
            setErrors({ submit: 'An unexpected error occurred' });
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleRegister = async (e) => {
        e.preventDefault();
        setErrors({});
        
        // Validate form
        const formErrors = validateForm();
        if (Object.keys(formErrors).length > 0) {
            setErrors(formErrors);
            return;
        }

        setIsSubmitting(true);
        
        try {
            const response = await fetch('http://localhost:8000/api/auth/register/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(credentials),
            });

            const data = await response.json();

            if (response.ok) {
                // Auto-login after successful registration
                const loginResult = await login(credentials);
                if (loginResult.success) {
                    navigate('/dashboard');
                }
            } else {
                setErrors({ submit: data.message || 'Registration failed' });
            }
        } catch (error) {
            setErrors({ submit: 'Network error. Please try again.' });
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleChange = (e) => {
        const { name, value } = e.target;
        setCredentials(prev => ({
            ...prev,
            [name]: value
        }));
        
        // Clear error when user starts typing
        if (errors[name]) {
            setErrors(prev => ({
                ...prev,
                [name]: ''
            }));
        }
    };

    return (
        <div className="login-container">
            <div className="login-card">
                <div className="login-header">
                    <h1>💰 Smart Expense Tracker</h1>
                    <p>Your personal finance companion</p>
                </div>

                <div className="login-tabs">
                    <button 
                        className={`tab-button ${!showRegister ? 'active' : ''}`}
                        onClick={() => setShowRegister(false)}
                    >
                        Login
                    </button>
                    <button 
                        className={`tab-button ${showRegister ? 'active' : ''}`}
                        onClick={() => setShowRegister(true)}
                    >
                        Register
                    </button>
                </div>

                <form onSubmit={showRegister ? handleRegister : handleSubmit} className="login-form">
                    {errors.submit && (
                        <div className="error-message">
                            {errors.submit}
                        </div>
                    )}

                    <div className="form-group">
                        <label htmlFor="username">Username</label>
                        <input
                            type="text"
                            id="username"
                            name="username"
                            value={credentials.username}
                            onChange={handleChange}
                            className={errors.username ? 'error' : ''}
                            placeholder="Enter your username"
                            disabled={isSubmitting}
                        />
                        {errors.username && (
                            <span className="field-error">{errors.username}</span>
                        )}
                    </div>

                    <div className="form-group">
                        <label htmlFor="password">Password</label>
                        <input
                            type="password"
                            id="password"
                            name="password"
                            value={credentials.password}
                            onChange={handleChange}
                            className={errors.password ? 'error' : ''}
                            placeholder="Enter your password"
                            disabled={isSubmitting}
                        />
                        {errors.password && (
                            <span className="field-error">{errors.password}</span>
                        )}
                    </div>

                    <button 
                        type="submit" 
                        className="login-button"
                        disabled={isSubmitting}
                    >
                        {isSubmitting ? (
                            <>
                                <span className="loading-spinner"></span>
                                {showRegister ? 'Creating Account...' : 'Signing In...'}
                            </>
                        ) : (
                            showRegister ? 'Create Account' : 'Sign In'
                        )}
                    </button>
                </form>

                <div className="login-footer">
                    <p>
                        {showRegister ? 'Already have an account?' : "Don't have an account?"}{' '}
                        <button 
                            className="link-button"
                            onClick={() => {
                                setShowRegister(!showRegister);
                                setErrors({});
                            }}
                        >
                            {showRegister ? 'Sign In' : 'Create Account'}
                        </button>
                    </p>
                </div>

                <div className="demo-credentials">
                    <h4>Demo Credentials:</h4>
                    <p>Username: <strong>demo</strong></p>
                    <p>Password: <strong>demo123</strong></p>
                </div>
            </div>
        </div>
    );
};

export default Login;