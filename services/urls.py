# services/urls.py (FINAL COMPLETE CODE - Dedicated URLs)
from django.urls import path
from . import views

app_name = 'services' 

urlpatterns = [
    path('', views.service_home, name='service_home'), 
    path('add/', views.add_service_request, name='add_service_request'),

    # Customer list
    path('my-requests/', views.customer_requests_list, name='customer_requests_list'),

    # Staff/Admin list 
    path('staff-list/', views.staff_requests_list, name='staff_requests_list'),

    # NEW DEDICATED CHAT URLS:
    # 1. Customer Chat URL
    path('<int:pk>/chat/', views.customer_service_request_chat, name='customer_chat'),
    
    # 2. Staff Chat URL
    path('staff/<int:pk>/chat/', views.staff_service_request_chat, name='staff_chat'),
]