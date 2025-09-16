import React, { useState, useEffect } from 'react';
import ExpenseService from './services/ExpenseService';
import './App.css';

function App() {
    const [expenses, setExpenses] = useState([]);
    const [stats, setStats] = useState({
        total_expenses: 0,
        today_expenses: 0,
        category_breakdown: {},
        recent_expenses: []
    });
    const [formData, setFormData] = useState({
        amount: '',
        description: ''
    });
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [isConnected, setIsConnected] = useState(false);
    const [message, setMessage] = useState('');

    // Test backend connection on component mount
    useEffect(() => {
        testBackendConnection();
        loadExpenses();
        loadStats();
    }, []);

    const testBackendConnection = async () => {
        try {
            const connected = await ExpenseService.testConnection();
            setIsConnected(connected);
            if (!connected) {
                setMessage('⚠️ Backend not connected. Make sure Django server is running on port 8000.');
            } else {
                setMessage('✅ Connected to Django backend with Excel storage!');
            }
        } catch (error) {
            setIsConnected(false);
            setMessage('❌ Failed to connect to backend');
        }
    };

    const loadExpenses = async () => {
        try {
            const expensesData = await ExpenseService.getExpenses();
            setExpenses(expensesData);
        } catch (error) {
            console.error('Error loading expenses:', error);
            setMessage('Error loading expenses: ' + error.message);
        }
    };

    const loadStats = async () => {
        try {
            const statsData = await ExpenseService.getExpenseStats();
            setStats(statsData);
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsSubmitting(true);
        setMessage('');

        try {
            // Validate form data
            if (!formData.amount || !formData.description) {
                setMessage('Please fill in both amount and description');
                return;
            }

            // Send to Django backend - will auto-categorize and save to Excel
            const result = await ExpenseService.addExpense({
                amount: parseFloat(formData.amount),
                description: formData.description.trim()
            });

            if (result.status === 'success') {
                // Reset form
                setFormData({ amount: '', description: '' });
                
                // Reload data
                await loadExpenses();
                await loadStats();
                
                setMessage(`✅ ${result.message} Category: ${result.expense.category}`);
            } else {
                setMessage('❌ Error saving expense: ' + result.message);
            }
        } catch (error) {
            setMessage('❌ Error: ' + error.message);
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleDownloadExcel = async () => {
        try {
            await ExpenseService.downloadExcel();
            setMessage('📊 Excel file downloaded successfully!');
        } catch (error) {
            setMessage('❌ Error downloading Excel file: ' + error.message);
        }
    };

    const formatCurrency = (amount) => {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR'
        }).format(amount);
    };

    return (
        <div className="app">
            <header className="app-header">
                <h1>💰 Smart Expense Tracker</h1>
                <div className="connection-status">
                    <span className={`status-indicator ${isConnected ? 'connected' : 'disconnected'}`}>
                        {isConnected ? '🟢' : '🔴'}
                    </span>
                    {isConnected ? 'Backend Connected' : 'Backend Disconnected'}
                </div>
            </header>

            {message && (
                <div className={`message ${message.includes('Error') || message.includes('❌') ? 'error' : 'success'}`}>
                    {message}
                </div>
            )}

            <div className="main-content">
                {/* Stats Dashboard */}
                <div className="stats-dashboard">
                    <div className="stat-card">
                        <h3>Total Expenses</h3>
                        <p className="stat-value">{formatCurrency(stats.total_expenses)}</p>
                    </div>
                    <div className="stat-card">
                        <h3>Today's Expenses</h3>
                        <p className="stat-value">{formatCurrency(stats.today_expenses)}</p>
                    </div>
                    <div className="stat-card">
                        <h3>Total Entries</h3>
                        <p className="stat-value">{expenses.length}</p>
                    </div>
                </div>

                {/* Add Expense Form */}
                <div className="expense-form-card">
                    <h2>Add New Expense</h2>
                    <form onSubmit={handleSubmit} className="expense-form">
                        <div className="form-group">
                            <label htmlFor="amount">Amount (₹)</label>
                            <input
                                type="number"
                                id="amount"
                                value={formData.amount}
                                onChange={(e) => setFormData({...formData, amount: e.target.value})}
                                placeholder="0.00"
                                required
                                min="0"
                                step="0.01"
                                disabled={!isConnected}
                            />
                        </div>
                        
                        <div className="form-group">
                            <label htmlFor="description">Description</label>
                            <input
                                type="text"
                                id="description"
                                value={formData.description}
                                onChange={(e) => setFormData({...formData, description: e.target.value})}
                                placeholder="e.g., Lunch at restaurant, Coffee with friends"
                                required
                                disabled={!isConnected}
                            />
                            <small>Tip: Include keywords like 'restaurant', 'uber', 'shopping' for auto-categorization</small>
                        </div>
                        
                        <div className="form-actions">
                            <button 
                                type="submit" 
                                disabled={isSubmitting || !isConnected}
                                className="btn btn-primary"
                            >
                                {isSubmitting ? 'Saving to Excel...' : 'Add Expense'}
                            </button>
                            
                            <button 
                                type="button"
                                onClick={handleDownloadExcel}
                                disabled={!isConnected || expenses.length === 0}
                                className="btn btn-secondary"
                            >
                                📊 Download Excel
                            </button>
                        </div>
                    </form>
                </div>

                {/* Category Breakdown */}
                {Object.keys(stats.category_breakdown).length > 0 && (
                    <div className="category-breakdown">
                        <h3>Expenses by Category</h3>
                        <div className="category-list">
                            {Object.entries(stats.category_breakdown).map(([category, amount]) => (
                                <div key={category} className="category-item">
                                    <span className="category-name">{category}</span>
                                    <span className="category-amount">{formatCurrency(amount)}</span>
                                    <div className="category-bar">
                                        <div 
                                            className="category-bar-fill" 
                                            style={{
                                                width: `${(amount / stats.total_expenses) * 100}%`,
                                                backgroundColor: getCategoryColor(category)
                                            }}
                                        ></div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Recent Expenses */}
                <div className="recent-expenses">
                    <h3>Recent Expenses</h3>
                    {expenses.length === 0 ? (
                        <p className="no-expenses">No expenses recorded yet. Add your first expense above!</p>
                    ) : (
                        <div className="expenses-list">
                            {stats.recent_expenses.map((expense) => (
                                <div key={expense.id} className="expense-item">
                                    <div className="expense-details">
                                        <span className="expense-description">{expense.description}</span>
                                        <span className="expense-category" style={{color: getCategoryColor(expense.category)}}>
                                            {expense.category}
                                        </span>
                                    </div>
                                    <div className="expense-meta">
                                        <span className="expense-amount">{formatCurrency(expense.amount)}</span>
                                        <span className="expense-date">{expense.date} {expense.time}</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );

    // Helper function for category colors
    function getCategoryColor(category) {
        const colors = {
            'Food': '#f59e0b',
            'Travel': '#6366f1', 
            'Shopping': '#10b981',
            'Entertainment': '#ec4899',
            'Bills': '#ef4444',
            'Healthcare': '#8b5cf6',
            'Education': '#06b6d4',
            'Others': '#64748b'
        };
        return colors[category] || '#64748b';
    }
}

export default App;