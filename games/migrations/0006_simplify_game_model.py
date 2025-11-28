# Generated manually to simplify Game model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0005_alter_gametoken_unique_together_and_more'),
    ]

    operations = [
        # Renomear retrogames_embed_url para rom_url
        migrations.RenameField(
            model_name='game',
            old_name='retrogames_embed_url',
            new_name='rom_url',
        ),
        # Remover relacionamento ManyToMany com Category
        migrations.RemoveField(
            model_name='game',
            name='categories',
        ),
        # Remover campo console
        migrations.RemoveField(
            model_name='game',
            name='console',
        ),
        # Remover campo is_visible (usaremos apenas is_active)
        migrations.RemoveField(
            model_name='game',
            name='is_visible',
        ),
        # Tornar description opcional (já está no modelo, mas garantindo na migração)
        migrations.AlterField(
            model_name='game',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='Descrição'),
        ),
    ]





