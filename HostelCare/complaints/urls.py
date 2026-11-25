from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    path('dashboard/warden/', views.warden_dashboard, name='warden_dashboard'),
    path('complaint/new/', views.create_complaint, name='create_complaint'),
    path('complaint/<int:pk>/', views.complaint_detail, name='complaint_detail'),
    path('complaint/<int:pk>/reopen/', views.reopen_complaint, name='reopen_complaint'),
]
