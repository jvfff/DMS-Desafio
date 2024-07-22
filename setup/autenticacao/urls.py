from django.urls import path
from .views import (
    RegisterView, VerifyCodeView, LoginView, HomeView, LogoutView,
    PasswordResetRequestView, PasswordResetVerifyView, PasswordResetCompleteView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify/', VerifyCodeView.as_view(), name='verify_code'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset-verify/', PasswordResetVerifyView.as_view(), name='password_reset_verify'),
    path('password-reset-complete/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('', HomeView.as_view(), name='home'),
]
