from django.urls import path
from . import views
from .views import (
    RegisterView, VerifyCodeView, LoginView, HomeView, LogoutView, 
    PasswordResetRequestView, PasswordResetVerifyView, PasswordResetCompleteView, 
    perfil_view, info_campo, reserva_detalhes, meus_pedidos, pedidos_recebidos, aprovar_reserva, recusar_reserva, deletar_campo_admin
)

urlpatterns = [
    path('registrar/', RegisterView.as_view(), name='register'),
    path('verify_code/', VerifyCodeView.as_view(), name='verify_code'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('password_reset/', views.PasswordResetRequestView.as_view(), name='password_reset'),
    path('password_reset_request/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password_reset_verify/', PasswordResetVerifyView.as_view(), name='password_reset_verify'),
    path('password_reset_complete/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('perfil/', perfil_view, name='perfil'),
    path('', HomeView.as_view(), name='home'),
    path('cadastrar-campo/', views.cadastrar_campo, name='cadastrar_campo'),
    path('gerenciar-campos/', views.gerenciar_campos, name='gerenciar_campos'),
    path('admin/gerenciar-campos/', views.admin_gerenciar_campos, name='admin_gerenciar_campos'),
    path('admin/aprovar-campo/<int:campo_id>/', views.aprovar_campo, name='aprovar_campo'),
    path('admin/recusar-campo/<int:campo_id>/', views.recusar_campo, name='recusar_campo'),
    path('editar-campo/<int:campo_id>/', views.editar_campo, name='editar_campo'),
    path('deletar-campo/<int:campo_id>/', views.deletar_campo, name='deletar_campo'),
    path('campo/info/<int:campo_id>/', info_campo, name='info_campo'),
    path('pesquisa/', views.pesquisa_campos, name='pesquisa_campos'),
    path('campo/<int:campo_id>/', views.detalhes_campo, name='detalhes_campo'),
    path('aprovar_reserva/<int:reserva_id>/', views.aprovar_reserva, name='aprovar_reserva'),
    path('reserva/detalhes/<int:campo_id>/', reserva_detalhes, name='reserva_detalhes'),
    path('meus-pedidos/', views.meus_pedidos, name='meus_pedidos'),
    path('pedidos-recebidos/', pedidos_recebidos, name='pedidos_recebidos'),
    path('aprovar-reserva/<int:reserva_id>/', aprovar_reserva, name='aprovar_reserva'),
    path('recusar-reserva/<int:reserva_id>/', recusar_reserva, name='recusar_reserva'),
    path('admin/deletar-campo/<int:campo_id>/', deletar_campo_admin, name='deletar_campo_admin'),
]
