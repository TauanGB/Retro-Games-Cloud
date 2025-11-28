# Generated manually to add API integration fields to GameRequest model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0012_remove_gamerequest_console_remove_gamerequest_notes_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='gamerequest',
            name='kickoff_id',
            field=models.CharField(blank=True, help_text='ID retornado pela API ao iniciar a busca do jogo', max_length=200, null=True, verbose_name='ID da Execução (Kickoff)'),
        ),
        migrations.AddField(
            model_name='gamerequest',
            name='execution_status',
            field=models.CharField(blank=True, help_text='Status atual da execução na API (pending, running, completed, failed)', max_length=50, null=True, verbose_name='Status da Execução'),
        ),
        migrations.AddField(
            model_name='gamerequest',
            name='ai_response_data',
            field=models.JSONField(blank=True, help_text='Dados completos retornados pela API após a busca do jogo', null=True, verbose_name='Dados Retornados pela IA'),
        ),
    ]

