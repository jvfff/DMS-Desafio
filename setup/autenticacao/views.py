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
from .forms import CustomUserCreationForm, VerificationForm, PasswordResetRequestForm, PasswordResetVerifyForm, PasswordResetCompleteForm, UserProfileForm, CampoForm, ReservaForm
from .models import UserProfile, Campo, Reserva

import random
from django.contrib.auth.decorators import login_required


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
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            user_email = form.cleaned_data.get('email')

            user_profile = UserProfile.objects.create(user=user)
            user_profile.verification_code = str(random.randint(100000, 999999))
            user_profile.save()

            subject = 'Código de Verificação'
            message = f'Seu código de verificação é {user_profile.verification_code}'
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user_email])

            messages.success(request, 'Verificação enviada para o email fornecido.')
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
            users = User.objects.filter(email=email)
            if users.exists():
                for user in users:
                    try:
                        user_profile = UserProfile.objects.get(user=user)
                        user_profile.reset_code = str(random.randint(100000, 999999))
                        user_profile.save()

                        subject = 'Código de Redefinição de Senha'
                        message = f'Seu código de redefinição de senha é {user_profile.reset_code}'
                        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])

                        messages.success(request, 'Código de redefinição de senha enviado para o email fornecido.')
                    except UserProfile.DoesNotExist:
                        messages.error(request, 'Perfil de usuário não encontrado para este usuário.')
                        continue
                return redirect('password_reset_verify')
            else:
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

@login_required
def perfil_view(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        field = request.POST.get('field')
        value = request.POST.get('value')
        if field and value:
            setattr(user_profile, field, value)
            user_profile.save()
            return redirect('perfil')
    else:
        form = UserProfileForm(instance=user_profile)

    return render(request, 'autenticacao/perfil.html', {'perfil': user_profile, 'form': form})

@login_required
def cadastrar_campo(request):
    if request.method == 'POST':
        form = CampoForm(request.POST, request.FILES)
        if form.is_valid():
            campo = form.save(commit=False)
            campo.latitude = request.POST.get('latitude')
            campo.longitude = request.POST.get('longitude')
            campo.usuario = request.user
            campo.save()
            return redirect('gerenciar_campos')
    else:
        form = CampoForm()
    return render(request, 'autenticacao/gerenciar_campos.html', {'form': form})

@login_required
def gerenciar_campos(request):
    if request.method == 'POST':
        form = CampoForm(request.POST, request.FILES)
        if form.is_valid():
            campo = form.save(commit=False)
            campo.usuario = request.user
            campo.save()
            return redirect('gerenciar_campos')
    else:
        form = CampoForm()

    campos = Campo.objects.filter(usuario=request.user)
    return render(request, 'autenticacao/gerenciar_campos.html', {'form': form, 'campos': campos})


@login_required
def admin_gerenciar_campos(request):
    if not request.user.is_superuser:
        return redirect('home')

    campos_pendentes = Campo.objects.filter(status='pendente')
    campos_aprovados = Campo.objects.filter(status='aprovado')
    return render(request, 'autenticacao/admin_gerenciar_campos.html', {
        'campos_pendentes': campos_pendentes,
        'campos_aprovados': campos_aprovados
    })

@login_required
def aprovar_campo(request, campo_id):
    campo = get_object_or_404(Campo, id=campo_id)
    campo.status = 'aprovado'
    campo.save()
    return redirect('admin_gerenciar_campos')

@login_required
def meus_pedidos(request):
    campos = Campo.objects.filter(usuario=request.user)
    return render(request, 'autenticacao/meus_pedidos.html', {'campos': campos})

@login_required
def recusar_campo(request, campo_id):
    campo = get_object_or_404(Campo, id=campo_id)
    campo.status = 'recusado'
    campo.save()
    return redirect('admin_gerenciar_campos')

@login_required
def editar_campo(request, campo_id):
    campo = get_object_or_404(Campo, id=campo_id, usuario=request.user)
    if request.method == 'POST':
        form = CampoForm(request.POST, instance=campo)
        if form.is_valid():
            form.save()
            return redirect('gerenciar_campos')
    else:
        form = CampoForm(instance=campo)
    return render(request, 'autenticacao/editar_campo.html', {'form': form, 'campo': campo})

@login_required
def deletar_campo(request, campo_id):
    campo = get_object_or_404(Campo, id=campo_id, usuario=request.user)
    if request.method == 'POST':
        campo.delete()
        return redirect('gerenciar_campos')
    return render(request, 'autenticacao/deletar_campo.html', {'campo': campo})

@login_required
def perfil(request):
    is_admin = request.user.is_superuser
    return render(request, 'autenticacao/perfil.html', {'is_admin': is_admin, 'perfil': request.user})

@login_required
def info_campo(request, campo_id):
    campo = get_object_or_404(Campo, id=campo_id)
    return render(request, 'autenticacao/info_campo.html', {'campo': campo})

@login_required
def lista_campos_aprovados(request):
    campos_aprovados = Campo.objects.filter(status='aprovado')
    return render(request, 'home/lista_campos_aprovados.html', {'campos': campos_aprovados})

from django.db.models import Q
from django.shortcuts import render

def pesquisa_campos(request):
    query = request.GET.get('q')
    vestiarios = request.GET.get('vestiarios')
    iluminacao = request.GET.get('iluminacao')
    tipo_gramado = request.GET.get('tipo_gramado')

    filtros = Q()

    if query:
        filtros &= Q(nome__icontains=query) | Q(localizacao__icontains=query)
    
    if vestiarios:
        if vestiarios == '4+':
            filtros &= Q(vestiarios__gte=4)
        else:
            filtros &= Q(vestiarios=vestiarios)
    
    if iluminacao:
        filtros &= Q(iluminacao=(iluminacao == 'sim'))
    
    if tipo_gramado:
        filtros &= Q(tipo_gramado=tipo_gramado)

    resultados = Campo.objects.filter(filtros)

    return render(request, 'home/lista_campos_aprovados.html', {'campos': resultados})

@login_required
def detalhes_campo(request, campo_id):
    campo = get_object_or_404(Campo, id=campo_id)
    
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.campo = campo
            reserva.usuario = request.user
            if reserva.tipo_reserva == 'hora':
                duracao = (reserva.hora_fim.hour - reserva.hora_inicio.hour)
                reserva.valor_total = duracao * campo.preco_por_hora
            else:
                reserva.valor_total = campo.preco_por_dia
            
            reserva.save()
            return redirect('meus_pedidos')
    else:
        form = ReservaForm()
    
    return render(request, 'autenticacao/detalhes_campo.html', {'campo': campo, 'form': form})


@login_required
def aprovar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)
    reserva.status = 'aprovado'
    reserva.save()
    return redirect('meus_pedidos')

@login_required
def reserva_detalhes(request, campo_id):
    campo = get_object_or_404(Campo, id=campo_id)
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.campo = campo
            reserva.usuario = request.user

            if reserva.tipo_reserva == 'hora':
                duracao = (reserva.hora_fim.hour - reserva.hora_inicio.hour)
                reserva.valor_total = duracao * campo.preco_por_hora
            else:
                reserva.valor_total = campo.preco_por_dia
            
            reserva.save()
            return redirect('meus_pedidos')
    else:
        form = ReservaForm()
    
    return render(request, 'autenticacao/reserva_detalhes.html', {'campo': campo, 'form': form})

@login_required
def meus_pedidos(request):
    reservas = Reserva.objects.filter(usuario=request.user).select_related('campo')
    return render(request, 'autenticacao/meus_pedidos.html', {'reservas': reservas})

@login_required
def pedidos_recebidos(request):
    pedidos = Reserva.objects.filter(campo__usuario=request.user, status='pendente').select_related('campo')
    return render(request, 'autenticacao/pedidos_recebidos.html', {'pedidos': pedidos})


@login_required
def recusar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)
    reserva.status = 'recusado'
    reserva.save()
    return redirect('pedidos_recebidos')

@login_required
def deletar_campo_admin(request, campo_id):
    if not request.user.is_superuser:
        return redirect('home')  

    campo = get_object_or_404(Campo, id=campo_id)
    campo.delete()
    return redirect('admin_gerenciar_campos')