from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # User / Student Request CRUD
    path('my-requests/', views.my_requests_view, name='my_requests'),
    path('request/new/', views.create_request_view, name='create_request'),
    path('request/<int:pk>/', views.request_detail_view, name='request_detail'),
    path('request/<int:pk>/edit/', views.edit_request_view, name='edit_request'),
    path('request/<int:pk>/delete/', views.delete_request_view, name='delete_request'),

    # Staff / Admin Dashboard & Management
    path('staff/', views.staff_dashboard_view, name='staff_dashboard'),
    path('staff/update/<int:pk>/', views.staff_update_status_view, name='staff_update_status'),
]
