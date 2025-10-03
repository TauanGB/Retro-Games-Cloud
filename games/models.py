from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
import secrets
import hashlib


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
    """Modelo para jogos individuais"""
    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(verbose_name="Descrição")
    console = models.CharField(max_length=50, verbose_name="Console")
    cover_image = models.URLField(verbose_name="URL da Capa", blank=True, null=True)
    rom_url = models.URLField(verbose_name="URL da ROM", blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço")
    categories = models.ManyToManyField(Category, verbose_name="Categorias", blank=True)
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Jogo"
        verbose_name_plural = "Jogos"
        ordering = ['title']

    def __str__(self):
        return self.title


class Plan(models.Model):
    """Modelo para planos de assinatura"""
    name = models.CharField(max_length=100, verbose_name="Nome do Plano")
    description = models.TextField(verbose_name="Descrição")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço Mensal")
    games = models.ManyToManyField(Game, verbose_name="Jogos Incluídos", blank=True)
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Plano"
        verbose_name_plural = "Planos"
        ordering = ['price']

    def __str__(self):
        return self.name


class Purchase(models.Model):
    """Modelo para compras de jogos individuais"""
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('completed', 'Concluída'),
        ('failed', 'Falhou'),
        ('cancelled', 'Cancelada'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuário")
    game = models.ForeignKey(Game, on_delete=models.CASCADE, verbose_name="Jogo")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Status")
    purchase_date = models.DateTimeField(auto_now_add=True, verbose_name="Data da Compra")
    idempotency_key = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="Chave de Idempotência")

    class Meta:
        verbose_name = "Compra"
        verbose_name_plural = "Compras"
        ordering = ['-purchase_date']

    def __str__(self):
        return f"{self.user.username} - {self.game.title} ({self.status})"


class Subscription(models.Model):
    """Modelo para assinaturas de planos"""
    STATUS_CHOICES = [
        ('active', 'Ativa'),
        ('cancelled', 'Cancelada'),
        ('expired', 'Expirada'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuário")
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, verbose_name="Plano")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="Status")
    start_date = models.DateTimeField(auto_now_add=True, verbose_name="Data de Início")
    current_period_end = models.DateTimeField(verbose_name="Fim do Período Atual")
    cancelled_at = models.DateTimeField(null=True, blank=True, verbose_name="Data de Cancelamento")
    idempotency_key = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="Chave de Idempotência")

    class Meta:
        verbose_name = "Assinatura"
        verbose_name_plural = "Assinaturas"
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.user.username} - {self.plan.name} ({self.status})"

    @property
    def is_active(self):
        """Verifica se a assinatura está ativa"""
        return (self.status == 'active' and 
                self.current_period_end > timezone.now())


class Entitlement(models.Model):
    """Modelo para direitos de acesso aos jogos"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuário")
    game = models.ForeignKey(Game, on_delete=models.CASCADE, verbose_name="Jogo")
    purchase = models.ForeignKey(Purchase, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Compra")
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Assinatura")
    granted_date = models.DateTimeField(auto_now_add=True, verbose_name="Data de Concessão")
    is_perpetual = models.BooleanField(default=False, verbose_name="Acesso Perpétuo")

    class Meta:
        verbose_name = "Direito de Acesso"
        verbose_name_plural = "Direitos de Acesso"
        unique_together = ('user', 'game')
        ordering = ['-granted_date']

    def __str__(self):
        source = "Perpétuo" if self.is_perpetual else f"Plano: {self.subscription.plan.name}"
        return f"{self.user.username} - {self.game.title} ({source})"

    def create_game_token(self):
        """Cria um token de acesso para este entitlement"""
        try:
            # Verificar se já existe um token ativo para este entitlement
            existing_token = GameToken.objects.filter(
                user=self.user,
                game=self.game,
                status='active'
            ).first()
            
            if existing_token:
                return existing_token
            
            # Criar novo token
            game_token = GameToken.objects.create(
                user=self.user,
                game=self.game,
                entitlement=self
            )
            
            return game_token
            
        except Exception as e:
            # Log do erro (em produção, usar logging)
            print(f"Erro ao criar token para entitlement {self.id}: {e}")
            return None

    def get_active_token(self):
        """Retorna o token ativo para este entitlement"""
        return GameToken.objects.filter(
            user=self.user,
            game=self.game,
            status='active'
        ).first()

    def revoke_token(self):
        """Revoga o token ativo para este entitlement"""
        token = self.get_active_token()
        if token:
            token.revoke()
            return True
        return False


class PaymentSession(models.Model):
    """Modelo para sessões de pagamento"""
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('completed', 'Concluída'),
        ('failed', 'Falhou'),
        ('cancelled', 'Cancelada'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuário")
    game = models.ForeignKey(Game, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Jogo")
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Plano")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor")
    session_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="ID da Sessão")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Status")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Data de Conclusão")

    class Meta:
        verbose_name = "Sessão de Pagamento"
        verbose_name_plural = "Sessões de Pagamento"
        ordering = ['-created_at']

    def __str__(self):
        item = self.game.title if self.game else self.plan.name
        return f"Sessão {self.session_id} - {item} ({self.status})"


class GameToken(models.Model):
    """Modelo para tokens de acesso aos jogos"""
    STATUS_CHOICES = [
        ('active', 'Ativo'),
        ('expired', 'Expirado'),
        ('revoked', 'Revogado'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuário")
    game = models.ForeignKey(Game, on_delete=models.CASCADE, verbose_name="Jogo")
    entitlement = models.ForeignKey(Entitlement, on_delete=models.CASCADE, verbose_name="Direito de Acesso")
    token = models.CharField(max_length=64, unique=True, editable=False, verbose_name="Token")
    token_hash = models.CharField(max_length=64, editable=False, verbose_name="Hash do Token")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="Status")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name="Data de Expiração")
    last_used_at = models.DateTimeField(null=True, blank=True, verbose_name="Último Uso")
    usage_count = models.PositiveIntegerField(default=0, verbose_name="Contador de Uso")
    
    class Meta:
        verbose_name = "Token de Jogo"
        verbose_name_plural = "Tokens de Jogos"
        ordering = ['-created_at']
        unique_together = ('user', 'game')

    def __str__(self):
        return f"Token {self.token[:8]}... - {self.user.username} - {self.game.title}"

    def save(self, *args, **kwargs):
        if not self.token:
            # Gerar token único
            self.token = self.generate_token()
            # Criar hash do token para armazenamento seguro
            self.token_hash = hashlib.sha256(self.token.encode()).hexdigest()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_token():
        """Gera um token único e seguro"""
        return secrets.token_urlsafe(32)

    def is_valid(self):
        """Verifica se o token é válido"""
        if self.status != 'active':
            return False
        
        if self.expires_at and timezone.now() > self.expires_at:
            self.status = 'expired'
            self.save()
            return False
            
        return True

    def mark_as_used(self):
        """Marca o token como usado"""
        self.last_used_at = timezone.now()
        self.usage_count += 1
        self.save()

    def revoke(self):
        """Revoga o token"""
        self.status = 'revoked'
        self.save()

    @classmethod
    def validate_token(cls, token, game_id=None):
        """Valida um token e retorna informações do jogo e usuário"""
        try:
            # Buscar token pelo hash
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            game_token = cls.objects.select_related('user', 'game', 'entitlement').get(
                token_hash=token_hash,
                status='active'
            )
            
            # Verificar se o token é válido
            if not game_token.is_valid():
                return None
                
            # Se game_id foi especificado, verificar se corresponde
            if game_id and game_token.game.id != game_id:
                return None
                
            # Marcar como usado
            game_token.mark_as_used()
            
            return {
                'valid': True,
                'user': game_token.user,
                'game': game_token.game,
                'entitlement': game_token.entitlement,
                'token': game_token
            }
            
        except cls.DoesNotExist:
            return None


# Método utilitário para adicionar funcionalidade ao modelo User
def user_has_game_access(user, game):
    """Verifica se o usuário tem acesso a um jogo específico"""
    return Entitlement.objects.filter(
        user=user,
        game=game
    ).exists()

def user_get_game_token(user, game):
    """Retorna o token ativo do usuário para um jogo específico"""
    entitlement = Entitlement.objects.filter(
        user=user,
        game=game
    ).first()
    
    if entitlement:
        return entitlement.get_active_token()
    return None

def user_create_game_token(user, game):
    """Cria um token para o usuário acessar um jogo específico"""
    entitlement = Entitlement.objects.filter(
        user=user,
        game=game
    ).first()
    
    if entitlement:
        return entitlement.create_game_token()
    return None

# Adicionar métodos ao modelo User
User.add_to_class('has_game_access', user_has_game_access)
User.add_to_class('get_game_token', user_get_game_token)
User.add_to_class('create_game_token', user_create_game_token)