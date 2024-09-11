from django.contrib.auth.models import User
from django.db import models
from django import forms

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    verification_code = models.CharField(max_length=6, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    reset_code = models.CharField(max_length=6, blank=True, null=True)
    nome = models.CharField(max_length=100, blank=True)
    cpf = models.CharField(max_length=14, blank=True)
    cep = models.CharField(max_length=9, blank=True)
    endereco = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)

    def __str__(self):
        return self.user.username

class Campo(models.Model):
    nome = models.CharField(max_length=200)
    localizacao = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    dias_disponiveis = models.TextField(blank=True, null=True, help_text="Dias disponíveis para aluguel (separados por vírgula)")
    horarios_disponiveis = models.TextField(blank=True, null=True, help_text="Horários disponíveis para aluguel (separados por vírgula)")
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    localizacao = models.CharField(max_length=255)
    tipo_gramado = models.CharField(max_length=50, choices=[('natural', 'Natural'), ('sintetico', 'Sintético')])
    iluminacao = models.BooleanField(default=False)
    vestiarios = models.IntegerField()
    largura = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Em metros")
    comprimento = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Em metros")
    capacidade = models.IntegerField(default=0) 
    facilidades = models.TextField(blank=True, null=True)  
    fotos = models.ImageField(upload_to='campos/fotos/', blank=True, null=True)
    preco_por_hora = models.DecimalField(max_digits=8, decimal_places=2, help_text="Preço por hora em R$")
    preco_por_dia = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, help_text="Preço por dia em R$ (opcional)")
    disponibilidade = models.TextField(blank=True, null=True, help_text="Informe os dias e horários disponíveis")
    descricao_adicional = models.TextField(blank=True, null=True, help_text="Informações adicionais sobre o campo")
    status = models.CharField(max_length=50, default='pendente')
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome
    
class Reserva(models.Model):
    campo = models.ForeignKey(Campo, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    data = models.DateField()
    hora_inicio = models.TimeField(null=True, blank=True)
    hora_fim = models.TimeField(null=True, blank=True)
    tipo_reserva = models.CharField(max_length=10, choices=[('hora', 'Por Hora'), ('dia', 'Por Dia')])
    status = models.CharField(max_length=20, default='pendente')
    valor_total = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    def __str__(self):
        if self.hora_inicio and self.hora_fim:
            return f"{self.usuario.username} - {self.campo.nome} em {self.data} das {self.hora_inicio} às {self.hora_fim}"
        return f"{self.usuario.username} - {self.campo.nome} em {self.data}"

class Avaliacao(models.Model):
    campo = models.ForeignKey(Campo, on_delete=models.CASCADE, related_name='avaliacoes')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    estrelas = models.PositiveSmallIntegerField(default=1, choices=[(i, str(i)) for i in range(1, 6)])
    comentario = models.TextField(blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.usuario.username} - {self.campo.nome} ({self.estrelas} estrelas)'
    
    class Meta:
        unique_together = ('campo', 'usuario')  

