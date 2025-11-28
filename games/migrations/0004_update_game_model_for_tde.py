# Generated manually for TDE restructuring
# Migration to update Game model: add slug, retrogames_embed_url, is_visible
# and remove price field (if exists)

from django.db import migrations, models
from django.utils.text import slugify


def populate_slugs(apps, schema_editor):
    """Preenche slugs para jogos existentes baseado no título"""
    Game = apps.get_model('games', 'Game')
    for game in Game.objects.filter(slug__isnull=True):
        base_slug = slugify(game.title)
        slug = base_slug
        counter = 1
        # Garantir que o slug seja único
        while Game.objects.filter(slug=slug).exclude(id=game.id).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        game.slug = slug
        game.save(update_fields=['slug'])


def reverse_populate_slugs(apps, schema_editor):
    """Operação reversa - não precisa fazer nada"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0003_gametoken'),
    ]

    operations = [
        # Adicionar campo slug (nullable inicialmente)
        migrations.AddField(
            model_name='game',
            name='slug',
            field=models.SlugField(blank=True, max_length=200, null=True, unique=True, verbose_name='Slug'),
        ),
        
        # Adicionar campo retrogames_embed_url (nullable - pode ser preenchido depois)
        migrations.AddField(
            model_name='game',
            name='retrogames_embed_url',
            field=models.URLField(blank=True, help_text='URL completa do embed do jogo no retrogames.cc. Ex: https://www.retrogames.cc/embed/[ID]', null=True, verbose_name='URL de Embed do Retrogames.cc'),
        ),
        
        # Adicionar campo is_visible
        migrations.AddField(
            model_name='game',
            name='is_visible',
            field=models.BooleanField(default=True, help_text='Se desmarcado, o jogo não aparecerá no catálogo público', verbose_name='Visível no Catálogo'),
        ),
        
        # Preencher slugs para registros existentes
        migrations.RunPython(populate_slugs, reverse_populate_slugs),
        
        # Remover campos antigos
        # Nota: Se os campos não existirem, você pode comentar estas linhas
        migrations.RemoveField(
            model_name='game',
            name='price',
        ),
        migrations.RemoveField(
            model_name='game',
            name='rom_url',
        ),
    ]

