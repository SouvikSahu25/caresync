from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='root'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('patient/', views.patient_dashboard, name='patient_dashboard'),
    path('doctor/', views.doctor_dashboard, name='doctor_dashboard'),
    path('book/', views.book_appointment, name='book_appointment'),
    path('update-appointment/<int:appointment_id>/', views.update_appointment, name='update_appointment'),
]
