from django import forms
from .models import GameRequest


class GameRequestForm(forms.ModelForm):
    """
    Formulário para usuários solicitarem a inclusão de um novo jogo ao catálogo.
    Apenas usuários autenticados podem usar este formulário.
    """
    
    title = forms.CharField(
        max_length=200,
        label="Título do Jogo",
        help_text="Nome do jogo que você deseja solicitar",
        widget=forms.TextInput(attrs={
            'class': 'modern-input',
            'placeholder': 'Ex: Super Mario World'
        })
    )
    
    details = forms.CharField(
        max_length=1000,
        label="Detalhes",
        help_text="Informações sobre o jogo solicitado",
        widget=forms.Textarea(attrs={
            'class': 'modern-input',
            'rows': 4,
            'placeholder': 'Aquele que tem um encanador que so cozinha a princesa pra tartarugona pegar ela'
        })
    )
    
    class Meta:
        model = GameRequest
        fields = ['title', 'details']


class AdminGameRequestForm(forms.ModelForm):
    """
    Formulário simplificado para administradores editarem a consulta para IA.
    A IA recebe apenas um texto simples e retorna de 1 a 5 nomes de jogos.
    """
    
    ai_query = forms.CharField(
        max_length=500,
        label="Texto para Busca na IA",
        help_text="Digite um texto simples descrevendo o jogo. Ex: 'Super Mario World SNES' ou 'jogo de plataforma com encanador'",
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'modern-input',
            'rows': 3,
            'placeholder': 'Ex: Super Mario World SNES ou jogo de plataforma com encanador'
        })
    )
    
    class Meta:
        model = GameRequest
        fields = ['ai_query']
        
