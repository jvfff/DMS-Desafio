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
from .forms import CustomUserCreationForm, VerificationForm, PasswordResetRequestForm, PasswordResetVerifyForm, PasswordResetCompleteForm, UserProfileForm, CampoForm, ReservaForm, AvaliacaoForm
from .models import UserProfile, Campo, Reserva, Avaliacao
import csv
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, SimpleDocTemplate
from reportlab.lib import colors, utils
from reportlab.lib.units import inch
from django.http import HttpResponse
from django.utils.crypto import get_random_string
import random
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_backends

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()

        backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user, backend=backend)
        
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
            request.session['user_data'] = {
                'username': form.cleaned_data.get('username'),
                'email': form.cleaned_data.get('email'),
                'password': form.cleaned_data.get('password1')
            }

            verification_code = str(random.randint(100000, 999999))
            request.session['verification_code'] = verification_code

            subject = 'Código de Verificação'
            message = f'Seu código de verificação é {verification_code}'
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [form.cleaned_data.get('email')])

            messages.success(request, 'Verificação enviada para o email fornecido.')
            return redirect('verify_code')

        return render(request, 'autenticacao/registrar.html', {'form': form})

class VerifyCodeLoginView(View):
    def get(self, request):
        form = VerificationForm()
        return render(request, 'autenticacao/verify_code.html', {'form': form})

    def post(self, request):
        form = VerificationForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data.get('code')
            session_code = request.session.get('verification_code')
            username = request.session.get('username')

            if code == session_code:
                try:
                    user = User.objects.get(username=username)

                    backend = 'django.contrib.auth.backends.ModelBackend'
                    login(request, user, backend=backend)

                    if 'verification_code' in request.session:
                        del request.session['verification_code']
                    if 'username' in request.session:
                        del request.session['username']

                    messages.success(request, 'Login bem-sucedido!')
                    return redirect('home')
                except User.DoesNotExist:
                    messages.error(request, 'Erro ao encontrar o usuário.')
            else:
                messages.error(request, 'Código inválido. Tente novamente.')

        return render(request, 'autenticacao/verify_code.html', {'form': form})

class VerifyCodeView(View):
    def get(self, request):
        form = VerificationForm()
        return render(request, 'autenticacao/verify_code.html', {'form': form})

    def post(self, request):
        form = VerificationForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data.get('code')
            session_code = request.session.get('verification_code')

            if code == session_code:
                user_data = request.session.get('user_data')

                if user_data:
                    user = User.objects.create_user(
                        username=user_data['username'],
                        email=user_data['email'],
                        password=user_data['password']
                    )
                    user.is_active = True  
                    user.save()

                    del request.session['verification_code']
                    del request.session['user_data']

                    backend = 'django.contrib.auth.backends.ModelBackend'
                    login(request, user, backend=backend)

                    messages.success(request, 'Conta criada e autenticada com sucesso!')
                    return redirect('home')
            else:
                messages.error(request, 'Código inválido. Tente novamente.')

        return render(request, 'autenticacao/verify_code.html', {'form': form})
    
class LoginView(View):
    def get(self, request):
        form = AuthenticationForm()
        return render(request, 'autenticacao/login.html', {'form': form})

    def post(self, request):
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()

            verification_code = str(random.randint(100000, 999999))
            request.session['verification_code'] = verification_code
            request.session['username'] = user.username

            subject = 'Código de Verificação para Login'
            message = f'Seu código de verificação é {verification_code}'
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

            messages.success(request, 'Código de verificação enviado para o seu e-mail.')
            return redirect('verify_code_login')

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
                    reset_code = str(random.randint(100000, 999999))
                    
                    try:
                        user_profile = UserProfile.objects.get(user=user)
                        user_profile.reset_code = reset_code
                        user_profile.save()
                    except UserProfile.DoesNotExist:
                        user_profile = UserProfile(user=user, reset_code=reset_code)
                        user_profile.save()

                    subject = 'Código de Redefinição de Senha'
                    message = f'Seu código de redefinição de senha é {reset_code}'
                    
                    print("Enviando e-mail para:", email)  
                    
                    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])

                    messages.success(request, 'Código de redefinição de senha enviado para o email fornecido.')
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

    subject = 'Aprovação do Campo: {}'.format(campo.nome)
    message = 'Olá, {}\n\nO seu campo "{}" foi aprovado com sucesso e já está disponível para reservas no sistema.'.format(campo.usuario.username, campo.nome)
    recipient_list = [campo.usuario.email]
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        recipient_list,
        fail_silently=False,  
    )

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

    horarios_disponiveis = campo.horarios_disponiveis.split(',') if campo.horarios_disponiveis else []

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

    return render(request, 'autenticacao/detalhes_campo.html', {
        'campo': campo,
        'form': form,
        'horarios_disponiveis': horarios_disponiveis  
    })



@login_required
def aprovar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)
    reserva.status = 'aprovado'
    reserva.save()

    subject = 'Confirmação de Reserva: {}'.format(reserva.campo.nome)
    message = (
    'Olá, {}\n\n'
    'Sua reserva para o campo "{}" foi confirmada para a data {}.\n'
    'Horário: {} às {}.\n'
    'Valor total: R$ {:.2f}.\n\n'
    'Obrigado por utilizar nossos serviços!'
    ).format(
        reserva.usuario.username,
        reserva.campo.nome,
        reserva.data.strftime('%d/%m/%Y'),
        reserva.hora_inicio.strftime('%H:%M') if reserva.hora_inicio else 'Não especificado',
        reserva.hora_fim.strftime('%H:%M') if reserva.hora_fim else 'Não especificado',
        reserva.valor_total if reserva.valor_total is not None else 0.0,
    )

    recipient_list = [reserva.usuario.email]

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        recipient_list,
        fail_silently=False,
    )

    return redirect('pedidos_recebidos')


@login_required
def reserva_detalhes(request, campo_id):
    campo = get_object_or_404(Campo, id=campo_id)
    avaliacoes = Avaliacao.objects.filter(campo=campo) 

    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.campo = campo
            reserva.usuario = request.user
            reserva.save()
            return redirect('meus_pedidos')
    else:
        form = ReservaForm()

    return render(request, 'autenticacao/reserva_detalhes.html', {
        'campo': campo,
        'avaliacoes': avaliacoes,  
        'form': form
    })

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

@login_required
def campo_detalhes(request, campo_id):
    campo = get_object_or_404(Campo, id=campo_id)
    avaliacoes = campo.avaliacoes.all()  

    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.campo = campo
            reserva.usuario = request.user
            if reserva.tipo_reserva == 'hora':
                duracao = reserva.hora_fim.hour - reserva.hora_inicio.hour
                reserva.valor_total = duracao * campo.preco_por_hora
            else:
                reserva.valor_total = campo.preco_por_dia
            reserva.save()
            return redirect('meus_pedidos')
    else:
        form = ReservaForm()

    return render(request, 'autenticacao/reserva_detalhes.html', {
        'campo': campo,
        'form': form,
        'avaliacoes': avaliacoes,  
    })


@login_required
def avaliar_campo(request, campo_id):
    campo = get_object_or_404(Campo, id=campo_id)
    avaliacao_existente = Avaliacao.objects.filter(campo=campo, usuario=request.user).first()

    if request.method == 'POST':
        form = AvaliacaoForm(request.POST, instance=avaliacao_existente)
        if form.is_valid():
            avaliacao = form.save(commit=False)
            avaliacao.campo = campo
            avaliacao.usuario = request.user
            avaliacao.save()
            return redirect('meus_pedidos')
    else:
        form = AvaliacaoForm(instance=avaliacao_existente)

    return render(request, 'autenticacao/avaliar_campo.html', {'campo': campo, 'form': form})

def gerar_relatorio_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="relatorio_campos.pdf"'

    p = SimpleDocTemplate(response, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("Relatório de Campos Alugados", styles['Title']))
    
    campos = Campo.objects.all()
    for campo in campos:
        elements.append(Paragraph(f"Campo: {campo.nome}", styles['Heading2']))
        elements.append(Paragraph(f"Localização: {campo.localizacao}", styles['BodyText']))
        
        reservas = Reserva.objects.filter(campo=campo)
        if reservas.exists():
            data = [["Usuário", "Data", "Duração", "Valor Total"]]  
            for reserva in reservas:
                duracao = f"{reserva.hora_inicio} - {reserva.hora_fim}" if reserva.hora_inicio and reserva.hora_fim else "Dia inteiro"
                data.append([reserva.usuario.username, reserva.data, duracao, f"R$ {reserva.valor_total:.2f}" if reserva.valor_total is not None else "R$ 0.00"])

            
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            elements.append(table)
        else:
            elements.append(Paragraph("Nenhuma reserva realizada.", styles['BodyText']))
        
        elements.append(Paragraph("<br/>", styles['BodyText']))  

    p.build(elements)
    return response


def wrap_text(text, width):
    return Paragraph(text, getSampleStyleSheet()['BodyText'])

def gerar_relatorio_pdf_campo(request, campo_id):
    campo = Campo.objects.get(id=campo_id)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="relatorio_campo_{campo.nome}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []
    
    styles = getSampleStyleSheet()
    
    elements.append(Paragraph(f"Relatório do Campo: {campo.nome}", styles['Title']))
    elements.append(Spacer(1, 12))
    
    dono_data = [
        ['Dono do Campo', 'Email Dono'],
        [campo.usuario.username, campo.usuario.email]
    ]
    
    dono_table = Table(dono_data, colWidths=[150, 300])
    dono_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    elements.append(dono_table)
    elements.append(Spacer(1, 20))

    reserva_data = [["Usuário", "Email Usuário", "Data", "Valor Total", "Tempo", "Aprovado"]]

    reservas = Reserva.objects.filter(campo=campo)
    
    for reserva in reservas:
        aprovado = "Sim" if reserva.status == "aprovado" else "Não"
        duracao = "Dia inteiro" if reserva.tipo_reserva == 'dia' else f"{reserva.hora_inicio} - {reserva.hora_fim}"
        reserva_data.append([
        reserva.usuario.username,
        reserva.usuario.email,
        reserva.data.strftime("%d/%m/%Y"),
        f"R$ {reserva.valor_total:.2f}" if reserva.valor_total is not None else "R$ 0.00",
        duracao,
        aprovado
    ])
    
    reserva_table = Table(reserva_data, colWidths=[80, 150, 80, 80, 100, 60])
    reserva_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    elements.append(Paragraph("Aluguéis:", styles['Heading2']))
    elements.append(reserva_table)
    
    doc.build(elements)
    return response


def gerar_relatorio_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="relatorio_campos.csv"'

    writer = csv.writer(response)
    writer.writerow(['Campo', 'Localização', 'Usuário', 'Data', 'Duração', 'Valor Total'])

    campos = Campo.objects.all()
    for campo in campos:
        reservas = Reserva.objects.filter(campo=campo)
        for reserva in reservas:
            duracao = f"{reserva.hora_inicio} - {reserva.hora_fim}" if reserva.hora_inicio and reserva.hora_fim else "Dia inteiro"
            writer.writerow([campo.nome, campo.localizacao, reserva.usuario.username, reserva.data, duracao, f"R$ {reserva.valor_total or 0:.2f}"])

    return response

def gerar_relatorio_csv_campo(request, campo_id):
    campo = Campo.objects.get(id=campo_id)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="relatorio_campo_{campo.nome}.csv"'

    writer = csv.writer(response)
    
    writer.writerow(['Relatório do Campo:', campo.nome])
    writer.writerow(['Dono do Campo:', campo.usuario.username])
    writer.writerow(['Email do Dono:', campo.usuario.email])
    writer.writerow([])  

    writer.writerow(['Usuário', 'Email Usuário', 'Data', 'Valor Total', 'Tempo', 'Aprovado'])

    reservas = Reserva.objects.filter(campo=campo)
    
    for reserva in reservas:
        aprovado = "Sim" if reserva.status == "aprovado" else "Não"
        duracao = "Dia inteiro" if reserva.tipo_reserva == 'dia' else f"{reserva.hora_inicio} - {reserva.hora_fim}"
        writer.writerow([
            reserva.usuario.username,
            reserva.usuario.email,
            reserva.data.strftime("%d/%m/%Y"),
            f"R$ {reserva.valor_total:.2f}" if reserva.valor_total is not None else "R$ 0.00",  
            duracao,
            "Sim" if reserva.status == "aprovado" else "Não"
        ])


    return response