from django.urls import path
from .views import (
    RegisterView, VerifyCodeView, LoginView, HomeView, LogoutView, 
    PasswordResetRequestView, PasswordResetVerifyView, PasswordResetCompleteView, 
    perfil_view
)

urlpatterns = [
    path('registrar/', RegisterView.as_view(), name='register'),
    path('verify_code/', VerifyCodeView.as_view(), name='verify_code'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('password_reset_request/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password_reset_verify/', PasswordResetVerifyView.as_view(), name='password_reset_verify'),
    path('password_reset_complete/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('perfil/', perfil_view, name='perfil'),
    path('', HomeView.as_view(), name='home'),
]