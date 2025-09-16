from django.urls import path
from . import views

urlpatterns = [
    path('expenses/', views.get_expenses, name='get_expenses'),
    path('expenses/add/', views.add_expense, name='add_expense'),
    path('expenses/stats/', views.get_expense_stats, name='get_expense_stats'),
    path('expenses/export/', views.export_excel, name='export_excel'),
    path('test/', views.test_connection, name='test_connection'),  # Test endpoint
]