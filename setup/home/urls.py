from django.urls import path
from .views import home_view
from autenticacao import views

urlpatterns = [
    path('', home_view, name='home'),
    path('campos-aprovados/', views.lista_campos_aprovados, name='lista_campos_aprovados'),
]
