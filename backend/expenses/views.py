import pandas as pd
import json
import os
from datetime import datetime
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

class ExpenseManager:
    def __init__(self, user_id):
        # Create user-specific excel files directory
        self.excel_dir = os.path.join(settings.BASE_DIR, 'excel_files')
        if not os.path.exists(self.excel_dir):
            os.makedirs(self.excel_dir)
        # Create user-specific Excel file
        self.excel_file_path = os.path.join(self.excel_dir, f'expenses_user_{user_id}.xlsx')
        
    def save_expense_to_excel(self, expense_data):
        """Save expense data to Excel file"""
        try:
            if os.path.exists(self.excel_file_path):
                df = pd.read_excel(self.excel_file_path)
            else:
                df = pd.DataFrame(columns=['id', 'amount', 'description', 'category', 'date', 'time', 'user_id'])
            
            new_expense = pd.DataFrame([expense_data])
            df = pd.concat([df, new_expense], ignore_index=True)
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
                df = df.fillna('')
                return df.to_dict('records')
            return []
        except Exception as e:
            print(f"Error reading from Excel: {e}")
            return []

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

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_expense(request):
    """API endpoint to add new expense - Now requires authentication"""
    try:
        # Get the authenticated user
        user = request.user
        expense_manager = ExpenseManager(user.id)
        
        data = request.data
        
        if not data.get('amount') or not data.get('description'):
            return Response({
                'status': 'error', 
                'message': 'Amount and description are required'
            }, status=400)
        
        category = categorize_expense(data.get('description', ''))
        
        expense_data = {
            'id': generate_expense_id(),
            'amount': float(data.get('amount', 0)),
            'description': data.get('description', '').strip(),
            'category': category,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'time': datetime.now().strftime('%H:%M'),
            'user_id': user.id
        }
        
        success = expense_manager.save_expense_to_excel(expense_data)
        
        if success:
            return Response({
                'status': 'success', 
                'expense': expense_data,
                'message': 'Expense saved to Excel successfully!'
            })
        else:
            return Response({
                'status': 'error', 
                'message': 'Failed to save expense to Excel'
            }, status=500)
            
    except Exception as e:
        return Response({
            'status': 'error', 
            'message': str(e)
        }, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_expenses(request):
    """API endpoint to get all expenses for authenticated user"""
    try:
        user = request.user
        expense_manager = ExpenseManager(user.id)
        expenses = expense_manager.get_expenses_from_excel()
        print(f"Retrieved {len(expenses)} expenses for user {user.username}")
        return Response({'status': 'success', 'expenses': expenses})
    except Exception as e:
        print(f"Error in get_expenses: {e}")
        return Response({'status': 'error', 'message': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_expense_stats(request):
    """API endpoint to get expense statistics for authenticated user"""
    try:
        user = request.user
        expense_manager = ExpenseManager(user.id)
        expenses = expense_manager.get_expenses_from_excel()
        
        if not expenses:
            return Response({
                'status': 'success',
                'stats': {
                    'total_expenses': 0,
                    'today_expenses': 0,
                    'category_breakdown': {},
                    'recent_expenses': [],
                    'total_count': 0
                }
            })
        
        today = datetime.now().strftime('%Y-%m-%d')
        total_expenses = sum(float(exp.get('amount', 0)) for exp in expenses)
        today_expenses = sum(float(exp.get('amount', 0)) for exp in expenses if exp.get('date') == today)
        
        category_breakdown = {}
        for expense in expenses:
            category = expense.get('category', 'Others')
            amount = float(expense.get('amount', 0))
            category_breakdown[category] = category_breakdown.get(category, 0) + amount
        
        recent_expenses = sorted(expenses, key=lambda x: str(x.get('date', '')) + str(x.get('time', '')), reverse=True)[:10]
        
        stats = {
            'total_expenses': total_expenses,
            'today_expenses': today_expenses,
            'category_breakdown': category_breakdown,
            'recent_expenses': recent_expenses,
            'total_count': len(expenses)
        }
        
        return Response({'status': 'success', 'stats': stats})
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_excel(request):
    """API endpoint to download Excel file for authenticated user"""
    try:
        user = request.user
        expense_manager = ExpenseManager(user.id)
        
        if os.path.exists(expense_manager.excel_file_path):
            with open(expense_manager.excel_file_path, 'rb') as f:
                response = HttpResponse(
                    f.read(),
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                filename = f'expenses_{user.username}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                return response
        else:
            return Response({'status': 'error', 'message': 'No expense data found'}, status=404)
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])  # Allow anyone to test connection
def test_connection(request):
    """Test endpoint to verify backend is working"""
    return Response({
        'status': 'success',
        'message': 'Backend is working!',
        'authenticated': request.user.is_authenticated,
        'user': request.user.username if request.user.is_authenticated else None,
        'timestamp': datetime.now().isoformat()
    })