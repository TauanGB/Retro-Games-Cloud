from django.db import models
from django.utils.text import slugify
from django.conf import settings


class Category(models.Model):
    """Modelo para categorias de jogos"""
    name = models.CharField(max_length=50, verbose_name="Nome da Categoria")
    description = models.TextField(verbose_name="Descrição", blank=True)
    color = models.CharField(max_length=7, default="#00d4ff", verbose_name="Cor (Hex)")
    icon = models.CharField(max_length=50, default="fas fa-gamepad", verbose_name="Ícone Font Awesome")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ['name']

    def __str__(self):
        return self.name


class Game(models.Model):
    """
    Modelo simplificado para jogos retro do catálogo do TDE.
    Cada jogo possui uma URL da ROM/jogo (retrogames.cc ou serviço similar) para ser exibido via iframe.
    """
    title = models.CharField(max_length=200, verbose_name="Título")
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True, verbose_name="Slug",
                           help_text="Será gerado automaticamente a partir do título se não fornecido")
    description = models.TextField(verbose_name="Descrição", blank=True, null=True)
    cover_image = models.URLField(
        verbose_name="URL da Imagem de Capa",
        blank=True, null=True,
        help_text="URL da imagem de capa do jogo (screenshot ou capa). Será exibida nos cards de jogos."
    )
    # URL da ROM/jogo no retrogames.cc ou serviço similar
    # Exemplo: https://www.retrogames.cc/embed/[ID_DO_JOGO]
    # Esta URL será usada diretamente no atributo src do iframe
    rom_url = models.URLField(
        verbose_name="URL da ROM/Jogo",
        blank=True, null=True,
        help_text="URL completa do jogo no retrogames.cc ou serviço similar. Ex: https://www.retrogames.cc/embed/[ID]. Esta URL será usada diretamente no iframe do emulador."
    )
    is_active = models.BooleanField(default=True, verbose_name="Ativo",
                                   help_text="Se desmarcado, o jogo não aparecerá no catálogo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Jogo"
        verbose_name_plural = "Jogos"
        ordering = ['title']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """Gera slug automaticamente se não fornecido"""
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Retorna a URL absoluta do jogo"""
        from django.urls import reverse
        return reverse('game_detail', kwargs={'slug': self.slug})


class GameRequest(models.Model):
    """
    Pedidos de usuários para que o administrador adicione novos jogos ao catálogo.
    Estes pedidos são apenas solicitações - nenhum jogo é criado automaticamente.
    O administrador deve avaliar cada pedido manualmente e, se aprovado, criar o jogo via Django Admin.
    """
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('approved', 'Aprovado'),
        ('rejected', 'Rejeitado'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Usuário",
        related_name='game_requests'
    )
    title = models.CharField(
        max_length=200,
        verbose_name="Título do Jogo",
        help_text="Nome do jogo que você deseja solicitar"
    )
    details = models.TextField(
        verbose_name="Detalhes do Jogo",
        help_text="Informações adicionais sobre o jogo solicitado",
        blank=True
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Status"
    )
    admin_note = models.TextField(
        max_length=500,
        verbose_name="Nota do Administrador",
        help_text="Justificativa ou observações do administrador sobre este pedido",
        blank=True
    )
    ai_query = models.CharField(
        max_length=500,
        verbose_name="Consulta para IA",
        help_text="Consulta/nome que será enviado para a IA para obter os dados completos do jogo. Será preenchido automaticamente com uma sugestão baseada no título e console, mas pode ser editado pelo administrador.",
        blank=True
    )
    ready_for_ai = models.BooleanField(
        default=False,
        verbose_name="Pronta para Enviar à IA",
        help_text="Indica se esta requisição está preparada e pronta para ser enviada à IA para processamento"
    )
    # Campos para integração com API externa
    kickoff_id = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="ID da Execução (Kickoff)",
        help_text="ID retornado pela API ao iniciar a busca do jogo"
    )
    execution_status = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Status da Execução",
        help_text="Status atual da execução na API (pending, running, completed, failed)"
    )
    ai_response_data = models.JSONField(
        blank=True,
        null=True,
        verbose_name="Dados Retornados pela IA",
        help_text="Dados completos retornados pela API após a busca do jogo"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    
    class Meta:
        verbose_name = "Pedido de Jogo"
        verbose_name_plural = "Pedidos de Jogos"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.user.username}) - {self.get_status_display()}"
    
    def save(self, *args, **kwargs):
        """Preenche automaticamente ai_query se estiver vazio"""
        if not self.ai_query and self.title:
            self.ai_query = f"{self.title} jogo retro"
        super().save(*args, **kwargs)
    
    def to_game_kwargs(self):
        """
        Retorna um dicionário com dados básicos que podem ser usados para criar um Game.
        Este método é apenas um helper - não cria o Game automaticamente.
        O administrador deve usar estas informações manualmente ao criar o jogo via Django Admin.
        """
        # Se houver dados da IA, usar eles; caso contrário, usar dados básicos
        if self.ai_response_data:
            return {
                'title': self.ai_response_data.get('title', self.title),
                'description': self.ai_response_data.get('description', f"Jogo solicitado por {self.user.username}. {self.details or ''}"),
                'rom_url': self.ai_response_data.get('rom_url') or self.ai_response_data.get('iframe_url'),
                'cover_image': self.ai_response_data.get('cover_image') or self.ai_response_data.get('image_url'),
            }
        return {
            'title': self.title,
            'description': f"Jogo solicitado por {self.user.username}. {self.details or ''}",
            'rom_url': None,
        }


# ============================================================================
# MODELOS LEGADOS - REMOVIDOS PARA O TDE
# ============================================================================
# Os seguintes modelos foram removidos pois não são mais necessários para
# o PWA educacional do TDE:
# - Plan (planos de assinatura)
# - Purchase (compras individuais)
# - Subscription (assinaturas)
# - Entitlement (direitos de acesso)
# - PaymentSession (sessões de pagamento)
# - GameToken (tokens de acesso)
#
# O sistema agora é um catálogo simples de jogos retro com acesso via
# iframe do retrogames.cc, sem necessidade de autenticação ou controle
# de acesso baseado em compras/assinaturas.
# ============================================================================