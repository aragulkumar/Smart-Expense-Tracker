from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views, auth_views

urlpatterns = [
    # Authentication endpoints
    path('auth/login/', auth_views.login_view, name='auth_login'),
    path('auth/register/', auth_views.register_view, name='auth_register'),
    path('auth/logout/', auth_views.logout_view, name='auth_logout'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/profile/', auth_views.user_profile_view, name='user_profile'),
    
    # Existing expense endpoints (now protected)
    path('expenses/', views.get_expenses, name='get_expenses'),
    path('expenses/add/', views.add_expense, name='add_expense'),
    path('expenses/stats/', views.get_expense_stats, name='get_expense_stats'),
    path('expenses/export/', views.export_excel, name='export_excel'),
    
    # Test endpoint (allow any)
    path('test/', views.test_connection, name='test_connection'),
]