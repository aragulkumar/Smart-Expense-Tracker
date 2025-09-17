import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

class ExpenseService {
    constructor() {
        this.api = axios.create({
            baseURL: API_BASE_URL,
            headers: {
                'Content-Type': 'application/json',
            },
            timeout: 10000,
        });

        // Add request interceptor to include auth token
        this.api.interceptors.request.use(
            (config) => {
                const token = localStorage.getItem('accessToken');
                if (token) {
                    config.headers.Authorization = `Bearer ${token}`;
                }
                return config;
            },
            (error) => {
                return Promise.reject(error);
            }
        );

        // Add response interceptor to handle token expiration
        this.api.interceptors.response.use(
            (response) => response,
            async (error) => {
                if (error.response?.status === 401) {
                    // Token expired, try to refresh or logout
                    const refreshToken = localStorage.getItem('refreshToken');
                    if (refreshToken) {
                        try {
                            const response = await axios.post(`${API_BASE_URL}/auth/refresh/`, {
                                refresh: refreshToken
                            });
                            
                            const newToken = response.data.access;
                            localStorage.setItem('accessToken', newToken);
                            
                            // Retry the original request
                            error.config.headers.Authorization = `Bearer ${newToken}`;
                            return axios.request(error.config);
                        } catch (refreshError) {
                            // Refresh failed, logout user
                            localStorage.removeItem('accessToken');
                            localStorage.removeItem('refreshToken');
                            localStorage.removeItem('userData');
                            window.location.href = '/login';
                        }
                    } else {
                        // No refresh token, logout user
                        localStorage.removeItem('accessToken');
                        localStorage.removeItem('refreshToken');
                        localStorage.removeItem('userData');
                        window.location.href = '/login';
                    }
                }
                return Promise.reject(error);
            }
        );
    }

    async addExpense(expenseData) {
        try {
            console.log('Adding expense:', expenseData);
            const response = await this.api.post('/expenses/add/', expenseData);
            return response.data;
        } catch (error) {
            console.error('Error adding expense:', error);
            throw new Error(
                error.response?.data?.message || 
                'Failed to add expense. Please try again.'
            );
        }
    }

    async getExpenses() {
        try {
            const response = await this.api.get('/expenses/');
            return response.data.expenses || [];
        } catch (error) {
            console.error('Error fetching expenses:', error);
            throw new Error('Failed to fetch expenses from backend');
        }
    }

    async getExpenseStats() {
        try {
            const response = await this.api.get('/expenses/stats/');
            return response.data.stats || {
                total_expenses: 0,
                today_expenses: 0,
                category_breakdown: {},
                recent_expenses: []
            };
        } catch (error) {
            console.error('Error fetching stats:', error);
            throw new Error('Failed to fetch expense statistics');
        }
    }

    async downloadExcel() {
        try {
            const response = await this.api.get('/expenses/export/', {
                responseType: 'blob'
            });
            
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            
            const today = new Date().toISOString().slice(0, 10);
            link.setAttribute('download', `expenses_export_${today}.xlsx`);
            
            document.body.appendChild(link);
            link.click();
            link.remove();
            window.URL.revokeObjectURL(url);
            
            return true;
        } catch (error) {
            console.error('Error downloading Excel:', error);
            throw new Error('Failed to download Excel file');
        }
    }

    async testConnection() {
        try {
            const response = await this.api.get('/expenses/');
            return response.status === 200;
        } catch (error) {
            return false;
        }
    }
}

export default new ExpenseService();