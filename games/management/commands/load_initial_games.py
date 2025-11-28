#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Management command Django para carregar jogos iniciais a partir de um arquivo JSON.

Propósito:
    Este comando lê um arquivo JSON chamado 'exemplos_iniciais.json' localizado na
    pasta 'data/' do projeto raiz e popula o banco de dados com os jogos contidos
    no arquivo.

Formato esperado do JSON:
    O arquivo deve conter uma lista de objetos, cada um representando um jogo:
    [
        {
            "name": "Nome do Jogo",
            "src": "https://www.retrogames.cc/embed/...",
            "image": "https://...",
            "description": "Descrição opcional do jogo"
        },
        ...
    ]

Mapeamento de campos JSON -> Modelo Game:
    - name -> title
    - src -> rom_url (URL da ROM/jogo no retrogames.cc)
    - image -> cover_image (URL da imagem de capa do jogo)
    - description -> description (opcional, será gerada automaticamente se não fornecido)
    - slug -> gerado automaticamente a partir do title
    - is_active -> True por padrão

Uso:
    # Carregar jogos (idempotente - não cria duplicatas)
    python manage.py load_initial_games

    # Limpar todos os jogos existentes antes de recarregar
    python manage.py load_initial_games --reset

Localização do arquivo:
    O arquivo JSON deve estar localizado em:
    <project_root>/data/exemplos_iniciais.json

    Se a pasta data/ não existir, ela será criada automaticamente (mas o arquivo
    deve ser criado manualmente).
"""

import json
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.conf import settings
from django.utils.text import slugify

from games.models import Game


class Command(BaseCommand):
    help = (
        'Carrega jogos iniciais a partir do arquivo JSON exemplos_iniciais.json. '
        'O arquivo deve estar localizado em data/exemplos_iniciais.json. '
        'O comando é idempotente e não cria jogos duplicados (usa slug como identificador único).'
    )

    # Caminho padrão do arquivo JSON (relativo ao BASE_DIR do Django)
    DEFAULT_JSON_PATH = 'data/exemplos_iniciais.json'

    def add_arguments(self, parser):
        """
        Adiciona argumentos opcionais ao comando.
        """
        parser.add_argument(
            '--json-file',
            type=str,
            help=f'Caminho alternativo para o arquivo JSON (padrão: {self.DEFAULT_JSON_PATH})',
        )
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Remove todos os jogos existentes antes de recarregar do JSON. '
                 'ATENÇÃO: Esta ação é destrutiva e não pode ser desfeita!',
        )

    def handle(self, *args, **options):
        """
        Método principal que executa o comando.
        """
        self.stdout.write(self.style.SUCCESS('=== CARREGANDO JOGOS INICIAIS ==='))
        
        # Determinar o caminho do arquivo JSON
        json_path = options.get('json_file') or self.DEFAULT_JSON_PATH
        
        # Converter para Path absoluto baseado no BASE_DIR
        if Path(json_path).is_absolute():
            json_file_path = Path(json_path)
        else:
            json_file_path = Path(settings.BASE_DIR) / json_path
        
        # Verificar se o arquivo existe
        if not json_file_path.exists():
            error_msg = (
                f'Arquivo exemplos_iniciais.json não encontrado em {json_file_path}. '
                f'Certifique-se de que o arquivo existe neste caminho ou use --json-file para '
                f'especificar um caminho alternativo.'
            )
            raise CommandError(self.style.ERROR(error_msg))
        
        # Carregar e validar JSON
        try:
            games_data = self.load_json_file(json_file_path)
            self.stdout.write(
                self.style.SUCCESS(f'Arquivo JSON carregado com sucesso. {len(games_data)} jogos encontrados.')
            )
        except json.JSONDecodeError as e:
            error_msg = (
                f'Erro ao decodificar JSON: {e}\n'
                f'O arquivo {json_file_path} não é um JSON válido. '
                f'Verifique a sintaxe do arquivo antes de tentar novamente.'
            )
            raise CommandError(self.style.ERROR(error_msg))
        except Exception as e:
            error_msg = f'Erro inesperado ao ler arquivo JSON: {e}'
            raise CommandError(self.style.ERROR(error_msg))
        
        # Processar jogos dentro de uma transação
        try:
            with transaction.atomic():
                # Opção --reset: limpar todos os jogos existentes
                if options.get('reset', False):
                    deleted_count = Game.objects.count()
                    Game.objects.all().delete()
                    self.stdout.write(
                        self.style.WARNING(
                            f'⚠️  RESET: {deleted_count} jogos foram removidos do banco de dados.'
                        )
                    )
                
                # Processar cada jogo do JSON
                created_count = 0
                updated_count = 0
                skipped_count = 0
                
                for index, game_data in enumerate(games_data, start=1):
                    try:
                        result = self.create_or_update_game(game_data, index)
                        if result == 'created':
                            created_count += 1
                        elif result == 'updated':
                            updated_count += 1
                        elif result == 'skipped':
                            skipped_count += 1
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(
                                f'❌ Erro ao processar jogo #{index} ({game_data.get("name", "sem nome")}): {e}'
                            )
                        )
                        skipped_count += 1
                
                # Exibir resumo
                self.stdout.write(self.style.SUCCESS('\n=== RESUMO ==='))
                self.stdout.write(f'✅ Jogos criados: {created_count}')
                self.stdout.write(f'🔄 Jogos atualizados: {updated_count}')
                self.stdout.write(f'⏭️  Jogos ignorados (com erro): {skipped_count}')
                self.stdout.write(f'📊 Total processado: {len(games_data)}')
                self.stdout.write(
                    self.style.SUCCESS(f'\n✅ Processamento concluído com sucesso!')
                )
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ ERRO FATAL: {e}'))
            raise CommandError(f'Falha ao processar jogos: {e}')

    def load_json_file(self, file_path):
        """
        Carrega e valida o arquivo JSON.
        
        Args:
            file_path: Caminho para o arquivo JSON
            
        Returns:
            list: Lista de dicionários contendo dados dos jogos
            
        Raises:
            json.JSONDecodeError: Se o JSON estiver malformado
            FileNotFoundError: Se o arquivo não existir
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Validar que é uma lista
        if not isinstance(data, list):
            raise ValueError('O JSON deve conter uma lista de objetos (array).')
        
        # Validar que cada item é um dicionário
        for i, item in enumerate(data):
            if not isinstance(item, dict):
                raise ValueError(f'Item #{i+1} do JSON não é um objeto válido.')
        
        return data

    def generate_description(self, game_title):
        """
        Gera uma descrição padrão para o jogo se não fornecida.
        
        Args:
            game_title: Título do jogo
            
        Returns:
            str: Descrição padrão
        """
        return f'Jogo retro clássico: {game_title}. Desfrute desta experiência nostálgica!'

    def create_or_update_game(self, game_data, index):
        """
        Cria ou atualiza um jogo no banco de dados.
        Usa slug como identificador único para garantir idempotência.
        
        Args:
            game_data: Dicionário com dados do jogo do JSON
            index: Índice do jogo na lista (para logs)
            
        Returns:
            str: 'created', 'updated' ou 'skipped'
        """
        # Extrair dados do JSON
        title = game_data.get('name', '').strip()
        if not title:
            self.stdout.write(self.style.WARNING(f'⚠️  Registro #{index}: Ignorado (sem título)'))
            return 'skipped'
        
        # Gerar slug a partir do título (usado como identificador único)
        slug = slugify(title)
        if not slug:
            self.stdout.write(
                self.style.WARNING(f'⚠️  Registro #{index}: Ignorado (não foi possível gerar slug a partir de "{title}")')
            )
            return 'skipped'
        
        # Extrair outros campos
        rom_url = game_data.get('src', '').strip()
        cover_image = game_data.get('image', '').strip()
        
        # Gerar descrição padrão se não fornecida
        description = game_data.get('description', '').strip()
        if not description:
            description = self.generate_description(title)
        
        # Buscar ou criar jogo usando slug como identificador único
        game, created = Game.objects.get_or_create(
            slug=slug,
            defaults={
                'title': title,
                'description': description,
                'cover_image': cover_image if cover_image else None,
                'rom_url': rom_url if rom_url else None,
                'is_active': True,
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'✅ [{index}] Criado jogo: {title}')
            )
            return 'created'
        else:
            # Jogo já existe - atualizar campos relevantes
            updated_fields = []
            
            if game.title != title:
                game.title = title
                updated_fields.append('title')
            
            if game.rom_url != rom_url and rom_url:
                game.rom_url = rom_url
                updated_fields.append('rom_url')
            
            if game.cover_image != cover_image and cover_image:
                game.cover_image = cover_image
                updated_fields.append('cover_image')
            
            # Atualizar descrição apenas se estiver vazia ou for a descrição padrão antiga
            if not game.description or game.description == self.generate_description(game.title):
                if description and description != self.generate_description(title):
                    game.description = description
                    updated_fields.append('description')
            
            # Garantir que está ativo
            if not game.is_active:
                game.is_active = True
                updated_fields.append('is_active')
            
            if updated_fields:
                game.save()
                self.stdout.write(
                    self.style.WARNING(
                        f'🔄 [{index}] Atualizado jogo: {title} - campos: {", ".join(updated_fields)}'
                    )
                )
                return 'updated'
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ [{index}] Jogo já existe (sem alterações): {title}'
                    )
                )
                return 'skipped'
