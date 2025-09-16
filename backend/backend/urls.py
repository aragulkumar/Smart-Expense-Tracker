from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

def home(request):
    return HttpResponse("Welcome to Smart Expense Tracker API 🚀")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("expenses.urls")),  # your API app
    path("", home),  # root URL
]
