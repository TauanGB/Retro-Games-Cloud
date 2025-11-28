from django.contrib import admin
from .models import Game, GameRequest


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    """Admin para jogos retro do catálogo"""
    list_display = ['title', 'slug', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'description', 'slug', 'cover_image']
    ordering = ['title']
    readonly_fields = ['slug', 'created_at', 'updated_at']
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('title', 'slug', 'description')
        }),
        ('Mídia', {
            'fields': ('cover_image',),
            'description': 'URL da imagem de capa do jogo. Será exibida nos cards de jogos.'
        }),
        ('Integração com Emulador', {
            'fields': ('rom_url',),
            'description': 'URL completa do jogo no retrogames.cc ou serviço similar. Ex: https://www.retrogames.cc/embed/[ID]. Esta URL será usada diretamente no atributo src do iframe do emulador.'
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
            ('Datas', {
                'fields': ('created_at', 'updated_at'),
                'classes': ('collapse',)
            }),
        )


@admin.register(GameRequest)
class GameRequestAdmin(admin.ModelAdmin):
    """Admin para pedidos de jogos enviados por usuários"""
    list_display = ['title', 'user', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['title', 'user__username', 'details']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    list_editable = ['status']
    
    fieldsets = (
        ('Informações do Pedido', {
            'fields': ('user', 'title')
        }),
        ('Detalhes Técnicos', {
            'fields': ('rom_url_suggestion', 'details')
        }),
        ('Análise Administrativa', {
            'fields': ('status', 'admin_note'),
            'description': 'Altere o status do pedido e adicione uma nota explicativa.'
        }),
        ('Datas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        """Torna user readonly após a criação"""
        if obj:  # editing an existing object
            return self.readonly_fields + ('user',)
        return self.readonly_fields