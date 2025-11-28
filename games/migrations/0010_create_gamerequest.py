# Generated manually to create GameRequest model
# This migration creates the complete GameRequest model as per the requirements

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('games', '0008_game_cover_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='GameRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Nome do jogo que você deseja solicitar', max_length=200, verbose_name='Título do Jogo')),
                ('console', models.CharField(help_text='Ex: SNES, GBA, PS1, N64, etc.', max_length=100, verbose_name='Console/Plataforma')),
                ('rom_url_suggestion', models.URLField(blank=True, help_text='URL da ROM no retrogames.cc ou link de referência do jogo', max_length=500, null=True, verbose_name='URL da ROM/Sugestão')),
                ('notes', models.TextField(blank=True, help_text='Informações adicionais sobre o jogo solicitado (opcional)', max_length=1000, verbose_name='Observações')),
                ('status', models.CharField(choices=[('pending', 'Pendente'), ('approved', 'Aprovado'), ('rejected', 'Rejeitado')], default='pending', max_length=20, verbose_name='Status')),
                ('admin_note', models.TextField(blank=True, help_text='Justificativa ou observações do administrador sobre este pedido', max_length=500, verbose_name='Nota do Administrador')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Data de Criação')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Última Atualização')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='game_requests', to=settings.AUTH_USER_MODEL, verbose_name='Usuário')),
            ],
            options={
                'verbose_name': 'Pedido de Jogo',
                'verbose_name_plural': 'Pedidos de Jogos',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='gamerequest',
            index=models.Index(fields=['status', '-created_at'], name='games_gamer_status_5f8a7b_idx'),
        ),
        migrations.AddIndex(
            model_name='gamerequest',
            index=models.Index(fields=['user', '-created_at'], name='games_gamer_user_id_8f2b3c_idx'),
        ),
    ]





