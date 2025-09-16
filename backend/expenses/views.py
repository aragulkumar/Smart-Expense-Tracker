import pandas as pd
import json
import os
from datetime import datetime
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings

class ExpenseManager:
    def __init__(self):
        # Create excel_files directory if it doesn't exist
        self.excel_dir = os.path.join(settings.BASE_DIR, 'excel_files')
        if not os.path.exists(self.excel_dir):
            os.makedirs(self.excel_dir)
        self.excel_file_path = os.path.join(self.excel_dir, 'expenses_data.xlsx')
        
    def save_expense_to_excel(self, expense_data):
        """Save expense data to Excel file"""
        try:
            # Try to read existing Excel file
            if os.path.exists(self.excel_file_path):
                df = pd.read_excel(self.excel_file_path)
            else:
                # Create new DataFrame if file doesn't exist
                df = pd.DataFrame(columns=['id', 'amount', 'description', 'category', 'date', 'time'])
            
            # Add new expense
            new_expense = pd.DataFrame([expense_data])
            df = pd.concat([df, new_expense], ignore_index=True)
            
            # Save to Excel
            df.to_excel(self.excel_file_path, index=False)
            return True
            
        except Exception as e:
            print(f"Error saving to Excel: {e}")
            return False
    
    def get_expenses_from_excel(self):
        """Read expenses from Excel file"""
        try:
            if os.path.exists(self.excel_file_path):
                df = pd.read_excel(self.excel_file_path)
                # Convert NaN to empty strings and ensure proper data types
                df = df.fillna('')
                return df.to_dict('records')
            return []
        except Exception as e:
            print(f"Error reading from Excel: {e}")
            return []

# Global expense manager instance
expense_manager = ExpenseManager()

def categorize_expense(description):
    """Auto-categorization logic using NLP keywords"""
    categories = {
        'Food': ['restaurant', 'coffee', 'lunch', 'dinner', 'breakfast', 'pizza', 'burger', 'grocery', 'food', 'cafe', 'meal', 'snack', 'eat'],
        'Travel': ['uber', 'taxi', 'bus', 'train', 'flight', 'gas', 'fuel', 'parking', 'metro', 'ola', 'auto', 'travel', 'trip'],
        'Shopping': ['amazon', 'mall', 'clothes', 'electronics', 'shoes', 'books', 'store', 'flipkart', 'shopping', 'buy', 'purchase'],
        'Entertainment': ['movie', 'cinema', 'game', 'concert', 'spotify', 'netflix', 'entertainment', 'music', 'show', 'theatre'],
        'Bills': ['electricity', 'water', 'internet', 'phone', 'rent', 'insurance', 'bill', 'utility', 'payment'],
        'Healthcare': ['doctor', 'medicine', 'hospital', 'pharmacy', 'medical', 'health', 'clinic', 'checkup'],
        'Education': ['course', 'books', 'tuition', 'fees', 'college', 'school', 'education', 'study', 'learning']
    }
    
    description_lower = description.lower()
    for category, keywords in categories.items():
        if any(keyword in description_lower for keyword in keywords):
            return category
    return 'Others'

def generate_expense_id():
    """Generate unique expense ID based on timestamp"""
    import time
    return int(time.time() * 1000)

@csrf_exempt
@require_http_methods(["POST"])
def add_expense(request):
    """API endpoint to add new expense"""
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        if not data.get('amount') or not data.get('description'):
            return JsonResponse({'status': 'error', 'message': 'Amount and description are required'})
        
        # Auto-categorize based on description
        category = categorize_expense(data.get('description', ''))
        
        expense_data = {
            'id': generate_expense_id(),
            'amount': float(data.get('amount', 0)),
            'description': data.get('description', '').strip(),
            'category': category,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'time': datetime.now().strftime('%H:%M')
        }
        
        # Save to Excel file
        success = expense_manager.save_expense_to_excel(expense_data)
        
        if success:
            return JsonResponse({
                'status': 'success', 
                'expense': expense_data,
                'message': 'Expense saved to Excel successfully!'
            })
        else:
            return JsonResponse({'status': 'error', 'message': 'Failed to save expense to Excel'})
            
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@require_http_methods(["GET"])
def get_expenses(request):
    """API endpoint to get all expenses"""
    try:
        expenses = expense_manager.get_expenses_from_excel()
        print(f"Retrieved {len(expenses)} expenses from Excel")  # Debug log
        return JsonResponse({'status': 'success', 'expenses': expenses})
    except Exception as e:
        print(f"Error in get_expenses: {e}")  # Debug log
        return JsonResponse({'status': 'error', 'message': str(e)})

@require_http_methods(["GET"])
def get_expense_stats(request):
    """API endpoint to get expense statistics"""
    try:
        expenses = expense_manager.get_expenses_from_excel()
        
        if not expenses:
            return JsonResponse({
                'status': 'success',
                'stats': {
                    'total_expenses': 0,
                    'today_expenses': 0,
                    'category_breakdown': {},
                    'recent_expenses': [],
                    'total_count': 0
                }
            })
        
        # Calculate statistics
        today = datetime.now().strftime('%Y-%m-%d')
        total_expenses = sum(float(exp.get('amount', 0)) for exp in expenses)
        today_expenses = sum(float(exp.get('amount', 0)) for exp in expenses if exp.get('date') == today)
        
        # Category breakdown
        category_breakdown = {}
        for expense in expenses:
            category = expense.get('category', 'Others')
            amount = float(expense.get('amount', 0))
            category_breakdown[category] = category_breakdown.get(category, 0) + amount
        
        # Recent expenses (last 10)
        recent_expenses = sorted(expenses, key=lambda x: str(x.get('date', '')) + str(x.get('time', '')), reverse=True)[:10]
        
        stats = {
            'total_expenses': total_expenses,
            'today_expenses': today_expenses,
            'category_breakdown': category_breakdown,
            'recent_expenses': recent_expenses,
            'total_count': len(expenses)
        }
        
        return JsonResponse({'status': 'success', 'stats': stats})
    except Exception as e:
        print(f"Error in get_expense_stats: {e}")  # Debug log
        return JsonResponse({'status': 'error', 'message': str(e)})

@require_http_methods(["GET"])
def export_excel(request):
    """API endpoint to download Excel file"""
    try:
        if os.path.exists(expense_manager.excel_file_path):
            with open(expense_manager.excel_file_path, 'rb') as f:
                response = HttpResponse(
                    f.read(),
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                filename = f'expenses_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                return response
        else:
            return JsonResponse({'status': 'error', 'message': 'No expense data found'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

# Test endpoint to check if backend is working
@require_http_methods(["GET"])
def test_connection(request):
    """Test endpoint to verify backend is working"""
    return JsonResponse({
        'status': 'success',
        'message': 'Backend is working!',
        'timestamp': datetime.now().isoformat()
    })