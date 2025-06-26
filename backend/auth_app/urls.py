from django.urls import path
from . import views

urlpatterns = [

      path('api/register/', views.RegisterView.as_view(), name='register'),
    path('api/login/', views.LoginView.as_view(), name='login'),
    path('api/profile/', views.ProfileView.as_view(), name='profile'),


]