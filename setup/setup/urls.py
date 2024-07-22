from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('autenticacao/', include('autenticacao.urls')),
    path('accounts/', include('allauth.urls')),  
    path('', include('home.urls')),  
    path('accounts/', include('allauth.urls')),
]