from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.views import View
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.contrib import messages
from .forms import CustomUserCreationForm, VerificationForm, PasswordResetRequestForm, PasswordResetVerifyForm, PasswordResetCompleteForm
from .models import UserProfile
import random

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('home')
    else:
        return render(request, 'autenticacao/activation_invalid.html')

class RegisterView(View):
    def get(self, request):
        form = CustomUserCreationForm()
        return render(request, 'autenticacao/registrar.html', {'form': form})

    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_active = False  
            user.save()
            user_email = form.cleaned_data.get('email')

            user_profile = UserProfile.objects.create(user=user)
            user_profile.verification_code = str(random.randint(100000, 999999))
            user_profile.save()

            subject = 'Código de Verificação'
            message = f'Seu código de verificação é {user_profile.verification_code}'
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user_email])

            return redirect('verify_code')
        return render(request, 'autenticacao/registrar.html', {'form': form})

class VerifyCodeView(View):
    def get(self, request):
        form = VerificationForm()
        return render(request, 'autenticacao/verify_code.html', {'form': form})

    def post(self, request):
        form = VerificationForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data.get('code')
            try:
                user_profile = UserProfile.objects.get(verification_code=code)
                user_profile.is_verified = True
                user_profile.user.is_active = True
                user_profile.user.save()
                user_profile.save()
                messages.success(request, 'Conta verificada com sucesso!')
                return redirect('login')
            except UserProfile.DoesNotExist:
                messages.error(request, 'Código de verificação inválido.')
        return render(request, 'autenticacao/verify_code.html', {'form': form})

class LoginView(View):
    def get(self, request):
        form = AuthenticationForm()
        return render(request, 'autenticacao/login.html', {'form': form})

    def post(self, request):
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
        return render(request, 'autenticacao/login.html', {'form': form})

class HomeView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'home.html')

class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('home')
    
class PasswordResetRequestView(View):
    def get(self, request):
        form = PasswordResetRequestForm()
        return render(request, 'autenticacao/password_reset_request.html', {'form': form})

    def post(self, request):
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            try:
                user = User.objects.get(email=email)
                user_profile = UserProfile.objects.get(user=user)
                user_profile.reset_code = str(random.randint(100000, 999999))
                user_profile.save()

                subject = 'Código de Redefinição de Senha'
                message = f'Seu código de redefinição de senha é {user_profile.reset_code}'
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])

                return redirect('password_reset_verify')
            except User.DoesNotExist:
                messages.error(request, 'Email não encontrado.')
        return render(request, 'autenticacao/password_reset_request.html', {'form': form})

class PasswordResetVerifyView(View):
    def get(self, request):
        form = PasswordResetVerifyForm()
        return render(request, 'autenticacao/password_reset_verify.html', {'form': form})

    def post(self, request):
        form = PasswordResetVerifyForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data.get('code')
            try:
                user_profile = UserProfile.objects.get(reset_code=code)
                request.session['reset_user_id'] = user_profile.user.id
                return redirect('password_reset_complete')
            except UserProfile.DoesNotExist:
                messages.error(request, 'Código de redefinição inválido.')
        return render(request, 'autenticacao/password_reset_verify.html', {'form': form})

class PasswordResetCompleteView(View):
    def get(self, request):
        user_id = request.session.get('reset_user_id')
        user = get_object_or_404(User, id=user_id)
        form = PasswordResetCompleteForm(user=user)
        return render(request, 'autenticacao/password_reset_complete.html', {'form': form})

    def post(self, request):
        user_id = request.session.get('reset_user_id')
        user = get_object_or_404(User, id=user_id)
        form = PasswordResetCompleteForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Senha redefinida com sucesso!')
            return redirect('login')
        return render(request, 'autenticacao/password_reset_complete.html', {'form': form})