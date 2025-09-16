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
                'Failed to connect to backend. Make sure Django server is running on port 8000.'
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